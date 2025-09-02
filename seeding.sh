#!/usr/bin/env bash
# seed.sh — Odoo 18 demo data seeder for your school models

# 🔧 EDIT THESE
ODOO_BIN="${ODOO_BIN:-odoo}"                     # or absolute path to odoo-bin
ODOO_CONF="${ODOO_CONF:-/path/to/odoo.conf}"     # <-- change me
DB="${DB:-my_school_db}"                         # <-- change me

set -euo pipefail

"$ODOO_BIN" shell -c "$ODOO_CONF" -d "$DB" <<'PYSEED'
import random, string, base64
from datetime import date, datetime, timedelta

# Faker is optional
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
    data_b64 = base64.b64encode(text.encode("utf-8")).decode("ascii")
    return env['ir.attachment'].create({
        'name': title,
        'type': 'binary',
        'datas': data_b64,
        'mimetype': 'text/plain',
    })

# ---------- knobs (feel free to tweak) ----------
SCHOOLS                 = 3
BRANCHES_PER_SCHOOL     = 2
TEACHERS_PER_SCHOOL     = 5
CLASSES_PER_SCHOOL      = 4
STUDENTS_PER_CLASS      = 10
AY_LIST                 = ["2023/2024", "2024/2025", "2025/2026"]  # respects your constraint
SEMESTER_NAMES          = ["S1", "S2"]
BOOK_PRODUCTS           = 6                                         # number of product.product "books"
SEED_TAG                = f"DEMO-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
# ------------------------------------------------

env = env  # odoo shell provides this

# helpers
def choose(lst):
    return random.choice(lst)

def safe_ref(xmlid, fallback=None):
    try:
        return env.ref(xmlid)
    except Exception:
        return fallback

# environment bits
company = env.company
currency = company.currency_id

# country/state (optional)
country = safe_ref('base.eg') or env['res.country'].search([], limit=1)
state = env['res.country.state'].search([('country_id', '=', country.id)], limit=1) or env['res.country.state'].search([], limit=1)

# ensure fee types (idempotent-ish by name)
fee_type_model = env['fee.type']
default_fee_types = [
    ('Tuition', 5000.0),
    ('Transport', 1200.0),
    ('Books', 800.0),
]
fee_types = []
for name, amount in default_fee_types:
    ft = fee_type_model.search([('name', '=', name)], limit=1)
    if not ft:
        ft = fee_type_model.create({'name': name, 'amount': amount})
    fee_types.append(ft)

# products (books) with book_level
book_levels = ['level_1','level_2']
book_products = []
for i in range(BOOK_PRODUCTS):
    lvl = choose(book_levels)
    p = env['product.product'].create({
        'name': f"{SEED_TAG} Book {i+1}",
        'list_price': random.choice([99, 149, 199, 249]),
        'type': 'consu',
        'book_level': lvl,
    })
    book_products.append(p)

# schools
schools = []
for si in range(SCHOOLS):
    s = env['school.school'].create({
        'name': f"{SEED_TAG} {rname('School')}",
        'address_id': False,
        'establishment_date': date.today() - timedelta(days=random.randint(365*5, 365*40)),
    })
    schools.append(s)

# branches (active/working) + tags + supervisors + history
branches = []
for s in schools:
    for bi in range(BRANCHES_PER_SCHOOL):
        b = env['school.branch'].create({
            'name': f"{SEED_TAG} {rname('Branch')}",
            'city_id': state.id if state else False,
            'country_id': country.id if country else False,
            'school_id': s.id,
            'working_type': 'working',
            'state': 'active',
            'opening_reason': "Auto-opened by seeder",
        })
        # tags (Many2many through school.branch.tags)
        for k in range(2):
            tag = env['school.branch.tags'].create({
                'name': f"{SEED_TAG} Tag {k+1}",
                'branch_id': b.id,
                'school_ids': [(4, s.id)],
            })
            # attach to branch.tags_ids via the many2many
            b.write({'tags_ids': [(4, tag.id)]})

        # supervisors (if there are internal users)
        internal_users = safe_ref('base.group_user')
        if internal_users:
            users = internal_users.users[:2]
            for u in users:
                env['school.branch.supervisors'].create({
                    'branch_id': b.id,
                    'user_id': u.id,
                })

        # history
        env['school.branch.history'].create({
            'branch_id': b.id,
            'created_by': env.user.id,
            'close_branch_reason': False,
            'open_branch_reason': "Initial open by seeder",
        })

        branches.append(b)

# academic years (linked to random branch)
academic_years = []
for ay_name in AY_LIST:
    for _ in range(max(1, SCHOOLS//1)):  # at least one per year
        ay = env['academic.year'].create({
            'name': ay_name,
            'branch_id': choose(branches).id if branches else False,
        })
        academic_years.append(ay)

# semesters (two per academic year)
semesters = []
for ay in academic_years:
    for nm in SEMESTER_NAMES:
        sem = env['school.semester'].create({
            'name': f"{nm}",
            'academic_year_id': ay.id,
        })
        semesters.append(sem)

# teachers (res.partner + school.teacher via _inherits)
teachers = []
for s in schools:
    for _ in range(TEACHERS_PER_SCHOOL):
        pname = f"{SEED_TAG} {person_name()}"
        partner = env['res.partner'].create({
            'name': pname,
            'email': email_for(pname),
        })
        t = env['school.teacher'].create({
            'partner_id': partner.id,
            'grade_level': choose(book_levels),
        })
        teachers.append(t)

# classes
classes = []
for s in schools:
    for _ in range(CLASSES_PER_SCHOOL):
        ay = choose(academic_years)
        sem = env['school.semester'].search([('academic_year_id', '=', ay.id)], limit=1) or choose(semesters)
        attach_for_class = []  # certificates optional
        c = env['school.class'].create({
            'name': f"{SEED_TAG} {rname('Class')}",
            'academic_year_id': ay.id,
            'semester_id': sem.id,
            'book_level': choose(['level_1','level_2']),
            'certificate_ids': [(6, 0, [a.id for a in attach_for_class])],
            'school_id': s.id,
            'teacher_id': choose(teachers).id if teachers else False,
            'state': 'draft',
        })
        classes.append(c)

# students (with required attachments!) and enrollments
# ensure the enrollment sequence exists
seq = env['ir.sequence'].search([('code','=','school.enrollment.seq')], limit=1)
if not seq:
    env['ir.sequence'].create({
        'name': 'School Enrollment Sequence',
        'code': 'school.enrollment.seq',
        'prefix': 'ENR/',
        'padding': 5,
    })

students = []
enrollments = []
grades = ['grade_1','grade_2','grade_3']

for c in classes:
    for _ in range(STUDENTS_PER_CLASS):
        sname = f"{SEED_TAG} {person_name()}"
        parent = env['res.partner'].create({'name': f"Parent of {sname}", 'email': email_for(sname)})
        # create small attachment to satisfy required=True
        att = make_attachment(env, f"{sname}-doc.txt", text=f"Demo doc for {sname}\n")
        st = env['school.student'].create({
            'name': sname,
            'parent_id': parent.id,
            'date_of_birth': date.today() - timedelta(days=random.randint(365*6, 365*18)),
            'national_id': ''.join(random.choices(string.digits, k=14)),
            'student_code': ''.join(random.choices(string.ascii_uppercase + string.digits, k=8)),
            'grade': choose(grades),
            'class_id': c.id,
            'attachment_ids': [(6, 0, [att.id])],  # REQUIRED by your model
        })
        students.append(st)

        ay = choose(academic_years)
        sem = env['school.semester'].search([('academic_year_id', '=', ay.id)], limit=1) or choose(semesters)
        enr = env['school.enrollment'].create({
            'parent_id': parent.id,
            'student_id': st.id,
            'semester_id': sem.id,
            'academic_year_id': ay.id,
            'class_id': c.id,
            'book_level': choose(['level_1','level_2']),
        })
        enrollments.append(enr)

# fee structures (+ lines) per BRANCH x (AY x SEM)
fee_structs = []
for b in branches:
    for ay in academic_years:
        sems_for_ay = env['school.semester'].search([('academic_year_id','=',ay.id)])
        for sem in sems_for_ay:
            fs = env['school.fee.structure'].create({
                'name': f"{SEED_TAG} Fees {b.name[-6:]}/{ay.name}/{sem.name}",
                'academic_year_id': ay.id,
                'semester_id': sem.id,
                'book_ids': [(6, 0, [p.id for p in random.sample(book_products, k=min(3, len(book_products)))])],
                'activation_date': date.today() - timedelta(days=random.randint(0, 90)),
                'currency_id': currency.id,
            })
            # one line per fee type (amount is related to fee.type.amount)
            lines_vals = []
            for ft in fee_types:
                lines_vals.append({
                    'name': f"{ft.name}",
                    'fee_type_id': ft.id,
                    'school_fee_id': fs.id,
                })
            env['fee.structure.lines'].create(lines_vals)
            fee_structs.append(fs)

print(f"✅ Seed done: {len(schools)} schools, {len(branches)} branches, "
      f"{len(academic_years)} AY, {len(semesters)} semesters, "
      f"{len(teachers)} teachers, {len(classes)} classes, "
      f"{len(students)} students, {len(enrollments)} enrollments, "
      f"{len(fee_types)} fee types, {len(fee_structs)} fee structures, {len(book_products)} books.")
PYSEED
