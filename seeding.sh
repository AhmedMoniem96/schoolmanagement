#!/usr/bin/env bash

ODOO_BIN="${ODOO_BIN:-/home/ahmed-moniem/odoo18/src/odoo-bin}"
ODOO_CONF="${ODOO_CONF:-/home/ahmed-moniem/odoo18/odoo.conf}"
DB="${DB:-odoo18_sar}"
# --------------------------------

set -euo pipefail

"$ODOO_BIN" shell -c "$ODOO_CONF" -d "$DB" <<'PYSEED'
import random, string, base64
from datetime import date, datetime, timedelta

# --- Make the tag obvious & searchable in UI ---
SEED_TAG = 'DEMO-SEED'

try:
    from faker import Faker
    fake = Faker()
except Exception:
    fake = None

def rname(prefix):
    if fake:
        return f"{prefix} " + fake.unique.word().title()
    return f"{prefix} " + ''.join(random.choices(string.ascii_uppercase, k=5))

def person_name():
    if fake: return fake.name()
    return " ".join([''.join(random.choices(string.ascii_uppercase, k=5)) for _ in range(2)])

def email_for(name):
    if fake: return fake.unique.email()
    return (name.lower().replace(' ', '.') + f"{random.randint(1,999)}@example.com")

def make_attachment(env, title, text="Demo file\n"):
    import base64
    data_b64 = base64.b64encode(text.encode("utf-8")).decode("ascii")
    return env['ir.attachment'].create({
        'name': title,
        'type': 'binary',
        'datas': data_b64,
        'mimetype': 'text/plain',
    })

# ---------- knobs ----------
SCHOOLS=3
BRANCHES_PER_SCHOOL=2
TEACHERS_PER_SCHOOL=5
CLASSES_PER_SCHOOL=4
STUDENTS_PER_CLASS=20
AY_LIST=["2024/2025","2025/2026"]
SEMESTER_NAMES=["S1","S2"]

BOOK_PRODUCTS=10
SUPPLIES_PRODUCTS=8
UNIFORM_PRODUCTS=5

INIT_BOOKS_PER_FS=3
INIT_SUPPLIES_PER_FS=3
INIT_UNIFORM_PER_FS=2

ENR_BOOKS_PER_STUDENT=2
ENR_SUPPLIES_PER_STUDENT=1
# ---------------------------

env = env
company = env.company
currency = company.currency_id

def safe_ref(xmlid, fallback=None):
    try:
        return env.ref(xmlid)
    except Exception:
        return fallback

# Products
book_levels = ['level_1','level_2']
book_products=[]; supplies_products=[]; uniform_products=[]

for i in range(BOOK_PRODUCTS):
    p=env['product.product'].create({
        'name': f"{SEED_TAG} Book {i+1}",
        'list_price': random.choice([99,149,199]),
        'type': 'consu',
        'book_level': random.choice(book_levels),
        'school_item_type': 'book',
    })
    book_products.append(p)

for i in range(SUPPLIES_PRODUCTS):
    p=env['product.product'].create({
        'name': f"{SEED_TAG} Supply {i+1}",
        'list_price': random.choice([30,50,75]),
        'type': 'consu',
        'school_item_type': 'supplies',
    })
    supplies_products.append(p)

for i in range(UNIFORM_PRODUCTS):
    p=env['product.product'].create({
        'name': f"{SEED_TAG} Uniform {i+1}",
        'list_price': random.choice([150,200,250]),
        'type': 'consu',
        'school_item_type': 'uniform',
    })
    uniform_products.append(p)

# Fee types
fee_types=[]
for nm,amt in [('Tuition',5000.0),('Transport',1200.0),('Activity',300.0)]:
    ft = env['fee.type'].search([('name','=',nm)], limit=1) or env['fee.type'].create({'name':nm, 'amount':amt})
    fee_types.append(ft)

# Simple school, branch, AY, semesters, teacher, class
school = env['school.school'].create({'name': f"{SEED_TAG} {rname('School')}", 'establishment_date': date.today()})
branch = env['school.branch'].create({'name': f"{SEED_TAG} {rname('Branch')}", 'school_id': school.id, 'working_type':'working','state':'active'})
ay = env['academic.year'].create({'name': AY_LIST[0], 'branch_id': branch.id})
sem1 = env['school.semester'].create({'name': SEMESTER_NAMES[0], 'academic_year_id': ay.id})
sem2 = env['school.semester'].create({'name': SEMESTER_NAMES[1], 'academic_year_id': ay.id})

partner = env['res.partner'].create({'name': f'{SEED_TAG} Teacher Partner', 'email': 'demo.teacher@example.com'})
teacher = env['school.teacher'].create({'partner_id': partner.id, 'grade_level': 'level_1'})
clazz = env['school.class'].create({'name': f"{SEED_TAG} Class A", 'academic_year_id': ay.id, 'semester_id': sem1.id,
                                    'book_level':'level_1','school_id': school.id,'teacher_id': teacher.id, 'state':'draft'})

# Students + enrollments
seq = env['ir.sequence'].search([('code','=','school.enrollment.seq')], limit=1) or env['ir.sequence'].create({
    'name':'School Enrollment Sequence','code':'school.enrollment.seq','prefix':'ENR/','padding':5
})
students=[]; enrollments=[]
for i in range(STUDENTS_PER_CLASS):
    sname = f"{SEED_TAG} Student {i+1}"
    parent = env['res.partner'].create({'name': f"Parent of {sname}", 'email': email_for(sname)})
    att = make_attachment(env, f"{sname}-doc.txt", f"Demo doc for {sname}\n")
    st = env['school.student'].create({
        'name': sname,'parent_id': parent.id,'date_of_birth': date(2015,1,1),
        'national_id': ''.join(random.choices(string.digits, k=14)),
        'student_code': ''.join(random.choices(string.ascii_uppercase + string.digits, k=8)),
        'grade':'grade_1','class_id': clazz.id,'attachment_ids': [(6,0,[att.id])],
    })
    students.append(st)
    enr = env['school.enrollment'].create({
        'parent_id': parent.id,'student_id': st.id,'semester_id': sem1.id,
        'academic_year_id': ay.id,'class_id': clazz.id,'book_level':'level_1',
    })
    enrollments.append(enr)

# Fee structure for AY/Sem1
fs = env['school.fee.structure'].create({
    'name': f"{SEED_TAG} Fees {ay.name}/{sem1.name}",
    'academic_year_id': ay.id,'semester_id': sem1.id,
    'books_ids':    [(6,0,[p.id for p in book_products[:INIT_BOOKS_PER_FS]])],
    'supplies_ids': [(6,0,[p.id for p in supplies_products[:INIT_SUPPLIES_PER_FS]])],
    'uniform_ids':  [(6,0,[p.id for p in uniform_products[:INIT_UNIFORM_PER_FS]])],
    'activation_date': date.today(),'currency_id': env.company.currency_id.id,
})
env['fee.structure.lines'].create([{
    'name': ft.name,'fee_type_id': ft.id,'school_fee_id': fs.id,
} for ft in fee_types])

# Per-enrollment enrich the cohort FS (add a book+ supply)
for enr in enrollments:
    extra_b = book_products[min(1, len(book_products)-1):min(2, len(book_products))] or []
    extra_s = supplies_products[min(1, len(supplies_products)-1):min(2, len(supplies_products))] or []
    fs.books_ids    = [(6,0,(fs.books_ids | env['product.product'].browse([p.id for p in extra_b])).ids)]
    fs.supplies_ids = [(6,0,(fs.supplies_ids | env['product.product'].browse([p.id for p in extra_s])).ids)]

# ---- PRINT SOME NAMES YOU CAN SEARCH IN UI ----
print("SCHOOLS:", env['school.school'].search([('name','ilike', 'DEMO-SEED')]).mapped('name')[:3])
print("FEE STRUCTURES:", env['school.fee.structure'].search([('name','ilike','DEMO-SEED')]).mapped('name')[:3])
print("STUDENTS:", env['school.student'].search([('name','ilike','DEMO-SEED')]).mapped('name')[:5])

# Force commit so data persists even if shell exits without auto-commit
env.cr.commit()
PYSEED
