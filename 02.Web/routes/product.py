import re
from flask import Blueprint, render_template, request, abort, redirect, url_for, current_app, flash
from extensions import db, login_manager
import pymysql

product_bp = Blueprint('product', __name__, url_prefix='/product')

#  ENUM 값 가져오기
def get_enum(table, column):
    conn = db.engine.raw_connection()
    cursor = conn.cursor()

    sql = """
        SELECT 
            COLUMN_TYPE FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_NAME = %s AND COLUMN_NAME = %s
    """
    cursor.execute(sql, (table, column))
    content = cursor.fetchone()
    cursor.close()
    conn.close()

    if content:
        return re.findall(r"'(.*?)'",content[0])
    return []
# ------------
#  첫 페이지
# ------------

@product_bp.route('/')
def list_product():
    # 1. 페이지 번호 파라미터 받기 (기본값 1)
    page = request.args.get('page', 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page

    #검색창 조건
    names = request.args.get('names','') # ID, 제품명 검색
    target = request.args.get('target','') # 타겟 해충
    status = request.args.get('status','') #판매중, 단종 상태
    
    # 드롭박스용 리스트 
    status_list = get_enum('PRODUCT','STATUS')

    #DB 연결
    conn = db.engine.raw_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)


# --- A. 전체 데이터 개수 조회 (페이지네이션 계산용) ---
    count_sql = "SELECT COUNT(*) as cnt FROM PRODUCT WHERE 1=1"
    count_params = []
    
    if names:
        count_sql += " AND (PRODUCT_NAME LIKE %s OR PRODUCT_ID LIKE %s)"
        count_params.extend([f"%{names}%", f"%{names}%"])
    if target:
        count_sql += " AND TARGET LIKE %s"
        count_params.append(f"%{target}%")
    if status:
        count_sql += " AND STATUS = %s"
        count_params.append(status)

    cursor.execute(count_sql, count_params)
    total_count = cursor.fetchone()['cnt']
    total_pages = (total_count + per_page - 1) // per_page  # 올림 계산

    # --- B. 현재 페이지 데이터 조회 ---
    sql = "SELECT PRODUCT_ID, PRODUCT_NAME, TARGET, PRICE_KOR, STATUS, DEV_DATE FROM PRODUCT WHERE 1=1"
    params = list(count_params) # 위에서 사용한 검색 조건 복사
    
    sql += " ORDER BY DEV_DATE DESC LIMIT %s OFFSET %s"
    params.extend([per_page, offset])
    
    # 실행
    cursor.execute(sql, params)
    products = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('2.product/product.html', products=products,
                                                    status_list=status_list,
                                                    page=page,
                                                    total_pages=total_pages,
                                                    total_count=total_count)

# ------------
#  제품 상세 페이지
# ------------
@product_bp.route('/<product_id>')
def product_detail(product_id):
    conn = db.engine.raw_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    sql = "SELECT * FROM PRODUCT WHERE PRODUCT_ID = %s"

    cursor.execute(sql,(product_id,))
    product = cursor.fetchone()

    cursor.close()
    conn.close()

    if not product:
        abort(404)
    
    return render_template('2.product/product_detail.html',
                           product=product)

# ------------
#  제품 등록 페이지
# ------------
import os
from datetime import datetime
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    """파일 확장자 체크 함수"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@product_bp.route('/register', methods=['GET', 'POST'])
def product_registration():
    if request.method == 'POST':
        # 1. 폼 데이터 수집
        p_id = request.form.get('product_id', '').strip()
        p_name = request.form.get('product_name', '').strip()
        target = request.form.get('target')
        currency = request.form.get('currency', 'KRW')
        price = request.form.get('price', 0)
        price_kor = request.form.get('price_kor', 0)
        cost = request.form.get('cost', 0)
        youtube = request.form.get('youtube')
        dev_date = datetime.now().strftime('%Y%m')
        memo = request.form.get('memo')

        # DB 연결 (사용자 시스템 사양에 최적화된 raw_connection)
        conn = db.engine.raw_connection()
        cursor = conn.cursor()

        try:
            # 2. 중복 ID 체크
            cursor.execute("SELECT PRODUCT_ID FROM PRODUCT WHERE PRODUCT_ID = %s", (p_id,))
            if cursor.fetchone():
                flash(f"에러: ID '{p_id}'는 이미 사용 중입니다.")
                return redirect(request.url)

            # 3. 이미지 파일 처리
            file = request.files.get('product_image')
            filename = None
            if file and file.filename != '':
                if allowed_file(file.filename):
                    ext = file.filename.rsplit('.', 1)[1].lower()
                    filename = f"{p_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{ext}"
                    upload_path = os.path.join(current_app.root_path, 'static', 'uploads', filename)
                    os.makedirs(os.path.dirname(upload_path), exist_ok=True)
                    file.save(upload_path)
                else:
                    flash("허용되지 않는 파일 형식입니다. (jpg, png, gif만 가능)")
                    return redirect(request.url)

            # 4. DB 데이터 저장
            sql = """
                INSERT INTO PRODUCT 
                (PRODUCT_ID, PRODUCT_NAME, TARGET, CURRENCY, PRICE, PRICE_KOR, COST, YOUTUBE, IMAGE, DEV_DATE, STATUS, MEMO)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'AVAILABLE', %s)
            """
            cursor.execute(sql, (p_id, p_name, target, currency, price, price_kor, cost, youtube, filename, dev_date, memo))
            
            #  conn 객체로 커밋
            conn.commit()
            flash(f"제품 '{p_name}' 등록 완료!")
            return redirect(url_for('product.list_product'))

        except Exception as e:
            #conn 객체로 롤백
            conn.rollback()
            flash(f"DB 오류가 발생했습니다: {str(e)}")
            return redirect(request.url)
            
        finally:
            
            cursor.close()
            conn.close()

    # GET 요청 시
    return render_template('2.product/product_registration.html')

# ------------
#  상품 삭제 페이지
# ------------

@product_bp.route('/delete/<product_id>')
def delete_product(product_id):
    conn = db.engine.raw_connection() 
    cursor = conn.cursor()
    
    try:
        # 삭제 SQL 실행
        sql = "DELETE FROM PRODUCT WHERE PRODUCT_ID = %s"
        cursor.execute(sql, (product_id,))
        conn.commit()
        
        flash(f"상품({product_id}) 정보가 삭제되었습니다.")
    except Exception as e:
        conn.rollback()
        flash(f"삭제 중 오류가 발생했습니다: {str(e)}")
    finally:
        cursor.close()
        conn.close()
        
    # 삭제 후 다시 목록 페이지로 돌아갑니다.
    return redirect(url_for('product.list_product'))