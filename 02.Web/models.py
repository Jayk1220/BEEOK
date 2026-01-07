from extensions import db
from flask_login import UserMixin
from datetime import datetime

# 1. 사용자 (USER)
class User(db.Model, UserMixin):
    __tablename__ = 'USER'
    sys_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    login_id = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('ADMIN', 'STAFF'), default='ADMIN')
    created_at = db.Column(db.DateTime, default=datetime.now)

    def get_id(self):
        return str(self.sys_id)

# 2. 고객 (CUSTOMER)
class Customer(db.Model):
    __tablename__ = 'CUSTOMER'
    customer_id = db.Column(db.String(20), primary_key=True)
    company_name = db.Column(db.String(50))
    contact_person = db.Column(db.String(50), nullable=False)
    contact = db.Column(db.String(50), nullable=False)
    status = db.Column(db.Enum('ACTIVE', 'DORMANT', 'INACTIVE'), default='ACTIVE')
    class_type = db.Column(db.Enum('CUSTOMER', 'VENDER'), name='class', default='CUSTOMER')

# 3. 고객 메모 (CUSTOMER_MEMO)
class CustomerMemo(db.Model):
    __tablename__ = 'CUSTOMER_MEMO'
    customer_id = db.Column(db.String(20), db.ForeignKey('CUSTOMER.customer_id'), primary_key=True)
    memo_no = db.Column(db.Integer, primary_key=True, default=1)
    memo_text = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.now)
    sys_id = db.Column(db.Integer, db.ForeignKey('USER.sys_id'), default=1)

# 4. 벌통 (HIVE)
class Hive(db.Model):
    __tablename__ = 'HIVE'
    hive_id = db.Column(db.String(50), primary_key=True)
    location = db.Column(db.String(20))
    frame_amount = db.Column(db.Integer, default=1)

# 5. 벌통 내검 (HIVE_INSPECTION)
class HiveInspection(db.Model):
    __tablename__ = 'HIVE_INSPECTION'
    ins_id = db.Column(db.String(50), primary_key=True)
    hive_id = db.Column(db.String(50), db.ForeignKey('HIVE.hive_id'))
    status_id = db.Column(db.Integer, db.ForeignKey('HIVE_STATUS.status_id'))
    ins_time = db.Column(db.DateTime, default=datetime.now)
    sys_id = db.Column(db.Integer, db.ForeignKey('USER.sys_id'), default=1)

# 6. 벌통 설치 (HIVE_INSTALL)
class HiveInstall(db.Model):
    __tablename__ = 'HIVE_INSTALL'
    hive_id = db.Column(db.String(50), db.ForeignKey('HIVE.hive_id'), primary_key=True)
    item_row = db.Column(db.Integer, primary_key=True, default=1)
    product_id = db.Column(db.String(20), db.ForeignKey('PRODUCT.product_id'))
    date = db.Column(db.Date, nullable=False)
    sys_id = db.Column(db.Integer, db.ForeignKey('USER.sys_id'), default=1)

# 7. 벌통 상태 종류 (HIVE_STATUS)
class HiveStatus(db.Model):
    __tablename__ = 'HIVE_STATUS'
    status_id = db.Column(db.Integer, primary_key=True)
    status_name = db.Column(db.String(50), nullable=False)

# 8. 벌통 로그 (HIVE_STATUS_LOG)
class HiveStatusLog(db.Model):
    __tablename__ = 'HIVE_STATUS_LOG'
    log_id = db.Column(db.String(50), primary_key=True)
    hive_id = db.Column(db.String(50), db.ForeignKey('HIVE.hive_id'))
    weight = db.Column(db.Numeric(5, 2))
    temp = db.Column(db.Numeric(5, 2))
    humi = db.Column(db.Numeric(5, 2))
    time = db.Column(db.DateTime, default=datetime.now)
    status_id = db.Column(db.Integer, db.ForeignKey('HIVE_STATUS.status_id'))

# 9. 제품 (PRODUCT)
class Product(db.Model):
    __tablename__ = 'PRODUCT'
    product_id = db.Column(db.String(20), primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Numeric(10, 2), default=0)
    cost = db.Column(db.Numeric(10, 0), default=0)
    status = db.Column(db.Enum('AVAILABLE', 'DISCONTINUED'), default='AVAILABLE')
    sys_id = db.Column(db.Integer, db.ForeignKey('USER.sys_id'), default=1)

# 10. 주문 (ORDERS)
class Orders(db.Model):
    __tablename__ = 'ORDERS'
    order_id = db.Column(db.String(100), primary_key=True)
    customer_id = db.Column(db.String(20), db.ForeignKey('CUSTOMER.customer_id'))
    date = db.Column(db.DateTime, default=datetime.now)
    fin_price = db.Column(db.Numeric(10, 2), nullable=False)
    payment = db.Column(db.Enum('CASH', 'CREDIT', 'TRANSFER'), nullable=False)
    sys_id = db.Column(db.Integer, db.ForeignKey('USER.sys_id'), default=1)

# 11. 주문 상세 (ORDER_DETAIL)
class OrderDetail(db.Model):
    __tablename__ = 'ORDER_DETAIL'
    order_id = db.Column(db.String(100), db.ForeignKey('ORDERS.order_id'), primary_key=True)
    order_row = db.Column(db.Integer, primary_key=True, default=1)
    product_id = db.Column(db.String(20), db.ForeignKey('PRODUCT.product_id'))
    amount = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)

# 12. 구매 (PURCHASE)
class Purchase(db.Model):
    __tablename__ = 'PURCHASE'
    purchase_id = db.Column(db.String(100), primary_key=True)
    customer_id = db.Column(db.String(20), db.ForeignKey('CUSTOMER.customer_id'))
    date = db.Column(db.DateTime, default=datetime.now)
    fin_price = db.Column(db.Numeric(10, 0), nullable=False)
    sys_id = db.Column(db.Integer, db.ForeignKey('USER.sys_id'), default=1)

# 13. 구매 상세 (PURCHASE_DETAIL)
class PurchaseDetail(db.Model):
    __tablename__ = 'PURCHASE_DETAIL'
    purchase_id = db.Column(db.String(100), db.ForeignKey('PURCHASE.purchase_id'), primary_key=True)
    purchase_row = db.Column(db.Integer, primary_key=True, default=1)
    product_id = db.Column(db.String(20), db.ForeignKey('PRODUCT.product_id'))
    price = db.Column(db.Numeric(10, 0), nullable=False)
    sys_id = db.Column(db.Integer, db.ForeignKey('USER.sys_id'), default=1)

# 14. 날씨 (WEATHER) - ★추가됨
class Weather(db.Model):
    __tablename__ = 'WEATHER'
    location = db.Column(db.String(50), primary_key=True)
    time = db.Column(db.DateTime, primary_key=True, default=datetime.now)
    temp = db.Column(db.Numeric(5, 2))
    humi = db.Column(db.Numeric(5, 2))
    data_from = db.Column(db.Enum('WEB', 'CHECK'), default='CHECK')

# 15. 제품 원가 로그
class ProductCostLog(db.Model):
    __tablename__ = 'PRODUCT_COST_LOG'
    product_id = db.Column(db.String(20), db.ForeignKey('PRODUCT.product_id'), primary_key=True)
    date = db.Column(db.Date, primary_key=True)
    cost = db.Column(db.Numeric(10, 0), nullable=False)
    sys_id = db.Column(db.Integer, db.ForeignKey('USER.sys_id'), default=1)

# 16. 제품 판매가 로그
class ProductPriceLog(db.Model):
    __tablename__ = 'PRODUCT_PRICE_LOG'
    product_id = db.Column(db.String(20), db.ForeignKey('PRODUCT.product_id'), primary_key=True)
    date = db.Column(db.Date, primary_key=True)
    price = db.Column(db.Numeric(10, 2))
    sys_id = db.Column(db.Integer, db.ForeignKey('USER.sys_id'), default=1)