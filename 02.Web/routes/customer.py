import re
from flask import Blueprint, render_template, request, abort
from extensions import db, login_manager
import pymysql

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
