import re
from flask import Blueprint, render_template, request, abort, flash, redirect, url_for
from extensions import db, login_manager
import pymysql
from datetime import datetime

customer_bp = Blueprint('customer', __name__, url_prefix='/customer')

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
@customer_bp.route('/')
def list_customer():
    #검색창 조건
    names = request.args.get('names','') # ID, 고객명, 상호명, 담당자명 검색
    contact = request.args.get('contact','') # email, 연락처
    address = request.args.get('address') #address, country
    status = request.args.get('status',"") #Active, 휴면 상태
    class_ = request.args.get('class_',"") #buyer, vendor

    # 드롭박스용 리스트 
    status_list = get_enum('CUSTOMER','STATUS')
    class_list = get_enum('CUSTOMER','CLASS')


    conn = db.engine.raw_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    # SQL
    sql = """ 
        SELECT
            CUSTOMER_ID, COMPANY_NAME, CONTACT_PERSON, CONTACT, EMAIL, REG_DATE, STATUS, CLASS 
        FROM CUSTOMER 
        WHERE 1=1 
       """ 
    params =[]

     #검색어 조건 추가
    if names:
        sql += " AND (CUSTOMER_ID LIKE %s OR COMPANY_NAME LIKE %s OR CONTACT_PERSON LIKE %s)"
        params.extend([f"%{names}%", f"%{names}%", f"%{names}%"])

    if contact:
        sql += " AND (EMAIL LIKE %s OR CONTACT LIKE %s)"
        params.extend([f"%{contact}%", f"%{contact}%"])

    if address:
        sql += " AND (COUNTRY LIKE %s OR ADDRESS LIKE %s)"
        params.extend([f"%{address}", f"%{address}"])

    if status:
        sql += " AND STATUS = %s"
        params.append(status)

    if class_:
        sql += " AND CLASS = %s"
        params.append(class_)
    
    # 정렬 순서
    sql += "ORDER BY STATUS, CLASS, REG_DATE DESC"

    cursor.execute(sql, params)
    customers = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('4.customer/customer.html', 
                            customers=customers, 
                            status_list=status_list, 
                            class_list=class_list,
                            names=names,
                            contact=contact,
                            address=address,
                            status=status,
                            class_=class_)

# ------------
#  고객 삭제 페이지
# ------------

@customer_bp.route('/delete/<customer_id>')
def delete_customer(customer_id):
    conn = db.engine.raw_connection() 
    cursor = conn.cursor()
    
    try:
        # 삭제 SQL 실행
        sql = "DELETE FROM CUSTOMER WHERE CUSTOMER_ID = %s"
        cursor.execute(sql, (customer_id,))
        conn.commit()
        
        flash(f"고객({customer_id}) 정보가 삭제되었습니다.")
    except Exception as e:
        conn.rollback()
        flash(f"삭제 중 오류가 발생했습니다: {str(e)}")
    finally:
        cursor.close()
        conn.close()
        
    # 삭제 후 다시 목록 페이지로 돌아갑니다.
    return redirect(url_for('customer.list_customer'))

# ------------
#  고객 등록 페이지
# ------------

@customer_bp.route('/registration', methods=['GET', 'POST'])
def customer_registration():
    class_list = get_enum('CUSTOMER', 'CLASS') # DB에서 ENUM 목록 가져오기

    if request.method == 'POST':
        # 1. 폼 데이터 수집
        c_id = request.form.get('customer_id', '').strip()
        business_no = request.form.get('business_no',"").strip()
        c_person = request.form.get('contact_person', '').strip()
        c_name = request.form.get('company_name', '').strip() or c_person
        contact = request.form.get('contact', '').strip()
        email = request.form.get('email', '').strip()
        address = request.form.get('address', '').strip()
        country = request.form.get('country', '한국').strip()
        bank = request.form.get('bank', '').strip()
        account_no = request.form.get('account_no', '').strip()
        account_name = request.form.get('account_name', '').strip()
        reg_date = datetime.now().strftime('%Y-%m-%d')
        memo = request.form.get('memo')
        status = "ACTIVE"
        c_class = request.form.get('class', 'CUSTOMER').upper()

        # DB 연결 (사용자 시스템 사양에 최적화된 raw_connection)
        conn = db.engine.raw_connection()
        cursor = conn.cursor()

        try:
            # 2. 중복 ID 체크
            cursor.execute("SELECT CUSTOMER_ID FROM CUSTOMER WHERE CUSTOMER_ID = %s", (c_id,))
            if cursor.fetchone():
                flash(f"에러: ID '{c_id}'는 이미 사용 중입니다.")
                return redirect(request.url)

            # 4. DB 데이터 저장
            sql = """
                        INSERT INTO CUSTOMER (
                            CUSTOMER_ID, COMPANY_NAME, BUSINESS_NO, CONTACT_PERSON, CONTACT, 
                            EMAIL, COUNTRY, ADDRESS, BANK, ACCOUNT_NO, 
                            ACCOUNT_NAME, REG_DATE, MEMO, STATUS, CLASS
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    
            cursor.execute(sql, (
                c_id, c_name, business_no, c_person, contact,
                email, country, address, bank, account_no,
                account_name, reg_date, memo, status, c_class
            ))
        
            conn.commit()
            flash("신규 고객 등록이 성공적으로 완료되었습니다.")
            return redirect(url_for('customer.list_customer'))

        except Exception as e:
            #conn 객체로 롤백
            conn.rollback()
            flash(f"DB 오류가 발생했습니다: {str(e)}")
            return redirect(request.url)
            
        finally:
            cursor.close()
            conn.close()

    # GET 요청 시
    return render_template('4.customer/customer_registration.html',
                            class_list=class_list)


# ------------
#  고객 상세 페이지
# ------------
@customer_bp.route('/<customer_id>', methods=['GET', 'POST'])
def customer_info(customer_id):
    conn = db.engine.raw_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    try:
        # 고객 정보 조회
        cursor.execute("SELECT * FROM CUSTOMER WHERE CUSTOMER_ID = %s", (customer_id))
        customer = cursor.fetchone()

        if not customer:
            abort(404)

        memo_sql = memo_sql = """
            SELECT MEMO_TEXT, DATE, SYS_ID 
            FROM CUSTOMER_MEMO 
            WHERE CUSTOMER_ID = %s 
            ORDER BY DATE DESC
        """
        cursor.execute(memo_sql, (customer_id,))
        memos = cursor.fetchall()

    finally:
        cursor.close()
        conn.close()
        
    return render_template('4.customer/customer_detail.html',
                           
                                                        memos=memos)