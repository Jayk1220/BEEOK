from flask import Blueprint, request, render_template
from flask_login import login_required, current_user
from extensions import db, login_manager
from datetime import datetime

#------------
# cursor.execute, render_template 추가하기
#-------------

# bp 이름 dashboard
dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/')
@login_required
def dashboard():
    # 날짜 
    #1. 기본 현재 연월
    now = datetime.now()
    now_year = now.year
    now_month = now.month
    
    #2. 선택 연월
    select_year = request.args.get('year',default=now_year,type=int)
    select_month = request.args.get('month',default=str(now_month)) #'전체' 월 있음

    params = [select_year]
    if select_month != '전체':
        params.append(int(select_month))
    
    # cursor 설정
    conn = db.engine.raw_connection()
    import pymysql
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    #3. 데이터 구성 
    #최상단 (날짜 설정에 관계 없이 실시간)

            # 이상 벌집 갯수(hive STATUS) 
    hive_status_sql = """
        SELECT 
            COUNT(DISTINCT HIVE_ID) AS TOTAL_HIVE, -- 전체 벌통 수
            SUM(CASE WHEN STATUS_ID = 1 THEN 0 ELSE 1 END) AS PROBLEM -- 상태이상
        FROM HIVE_STATUS_LOG
        WHERE (HIVE_ID, TIME) IN (
            SELECT HIVE_ID, MAX(TIME) AS TIME
            FROM HIVE_STATUS_LOG
            GROUP BY HIVE_ID
            );
            """
    cursor.execute(hive_status_sql)
    hive_status = cursor.fetchone()
    
            #벌집 온도 이상 (추후 구현)

            #벌집 습도 이상 (추후 구현)

    # 상단 ( order#, 매출액)
        #주문건수, 매출액
    order_qty_sql = """
        SELECT 
            COUNT(ORDER_ID) AS ORDER_QTY,
            IFNULL(SUM(FIN_PRICE), 0) AS TOTAL_SALES
        FROM ORDERS
        WHERE YEAR(DATE) = %s
            AND STATUS NOT IN ('CANCELLED')
        """
    if select_month != '전체':
        order_qty_sql += " AND MONTH(DATE) = %s"
        cursor.execute(order_qty_sql, params)
        total_data = cursor.fetchone()
    

    # 왼쪽 (주문 관련)
    order_sql = """
    SELECT ORDER_ID, STATUS
    FROM ORDERS
    WHERE YEAR(DATE) = %s
        AND STATUS NOT IN ('DELIVERED','CANCELLED')
    """

    if select_month != '전체':
        order_sql += " AND MONTH(DATE) = %s"
    order_sql += " ORDER BY DATE DESC"
    cursor.execute(order_sql, params)
    orders = cursor.fetchall()


    # 오른쪽 (이번달 판매 제품 순위)
    product_sql = """
    SELECT P.PRODUCT_NAME, SUM(OD.AMOUNT) AS TOTAL_QTY
    FROM ORDER_DETAIL OD
    JOIN PRODUCT P ON OD.PRODUCT_ID = P.PRODUCT_ID
    JOIN ORDERS O ON OD.ORDER_ID = O.ORDER_ID
    WHERE YEAR(O.DATE) = %s
        AND O.STATUS NOT IN ('CANCELLED')
    """
    if select_month != '전체':
        product_sql += " AND MONTH(O.DATE) = %s"
    product_sql += """ GROUP BY p.PRODUCT_ID, p.PRODUCT_NAME
                    ORDER BY TOTAL_QTY DESC"""
    cursor.execute(product_sql, params)
    rankings = cursor.fetchall()

    # 가운데 (그래프 그리기)
    
        #매출액
        #주문건수



    return render_template('1.dashboard/dashboard.html',
                            hive=hive_status,      # 실시간 벌통 정보
                            total=total_data,      # 상단 매출/건수 요약
                            orders=orders,         # 왼쪽 미완료 주문 목록
                            rankings=rankings,     # 오른쪽 인기 상품 TOP 5
                                                   # 가운데 그래프용 데이터
                            now_year=now_year,     # 날짜 선택기용
                            select_year=select_year,
                            select_month=select_month)