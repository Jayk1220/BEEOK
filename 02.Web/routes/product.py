from flask import Blueprint, render_template, request
from extensions import db, login_manager
import pymysql

product_bp = Blueprint('product', __name__, url_prefix='/product')

# ------------
#  첫 페이지
# ------------

@product_bp.route('/')
def list_product():
    #DB 연결
    conn = db.engine.raw_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)


# 제품 목록 쿼리 (아버님 DB 테이블명에 맞춰 수정 필요)
    sql = "SELECT PRODUCT_ID, PRODUCT_NAME, TARGET, PRICE_KOR FROM product"
    cursor.execute(sql)
    products = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('2.product/product.html', products=products)

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
        return "해당 제품을 찾을 수 없습니다", 404