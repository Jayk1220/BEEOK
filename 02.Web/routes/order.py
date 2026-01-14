from flask import Blueprint, render_template, request, abort, redirect, url_for, current_app, flash
from extensions import db, login_manager
import pymysql

order_bp = Blueprint('order', __name__, url_prefix='/order')

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

@order_bp.route('/')
def list_order():
    #검색창 조건
    order = request.args.get('order_id','') # 주문번호
    names = request.args.get('names','') # 고객명 고객ID 검색
    status = request.args.get('status','') #주문상태
    
    # 드롭박스용 리스트 
    status_list = get_enum('ORDER','STATUS')

    #DB 연결
    conn = db.engine.raw_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)


    # 제품 목록 쿼리
    sql = "SELECT ORDER_ID, CUSTOMER_ID, DATE, STATUS FROM ORDERS WHERE 1=1"
    params = []

    #검색어 조건 추가

    if order:
        sql += " AND ORDER_ID LIKE %s"
        params.append(f"%{order}%")

    #고객 이름/ID
    if names :
        sql += " AND (CUSTOMER_ID LIKE %s OR CUSTOMER_NAME LIKE %s)"
        params.extend([f"%{names}%",f"%{names}%"])

    # 상태
    if status:
        sql += " AND STATUS = %s"
        params.append(status)
    
    sql += " ORDER BY STATUS DESC"
    
    # 실행
    cursor.execute(sql, params)
    products = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('3.order/order.html', products=products,
                                                    status_list=status_list)
