from flask import Flask, render_template, request, redirect, url_for
from database import initialize_database, get_db_connection

app = Flask(__name__)

initialize_database()


# =========================
# DASHBOARD
# =========================

@app.route("/")
def home():

    conn = get_db_connection()

    student_count = conn.execute(
        "SELECT COUNT(*) FROM students"
    ).fetchone()[0]

    relation_count = conn.execute(
        "SELECT COUNT(*) FROM relations"
    ).fetchone()[0]

    conn.close()

    return render_template(
        "index.html",
        student_count=student_count,
        relation_count=relation_count
    )


# =========================
# STUDENTS
# =========================

@app.route("/students")
def students():

    conn = get_db_connection()

    students = conn.execute(
        "SELECT * FROM students ORDER BY id DESC"
    ).fetchall()

    conn.close()

    return render_template(
        "students.html",
        students=students
    )


@app.route("/add_student", methods=["POST"])
def add_student():

    name = request.form["name"]
    branch = request.form["branch"]
    year = request.form["year"]

    conn = get_db_connection()

    conn.execute(
        """
        INSERT INTO students (name, branch, year)
        VALUES (?, ?, ?)
        """,
        (name, branch, year)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("students"))


@app.route("/delete_student/<int:student_id>")
def delete_student(student_id):

    conn = get_db_connection()

    conn.execute(
        "DELETE FROM students WHERE id = ?",
        (student_id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("students"))


# =========================
# RELATIONS
# =========================

@app.route("/relations")
def relations():

    conn = get_db_connection()

    students = conn.execute(
        "SELECT * FROM students ORDER BY name"
    ).fetchall()

    relations = conn.execute("""
        SELECT
            relations.id,
            s1.name AS student1,
            s2.name AS student2,
            relations.relation_type
        FROM relations
        JOIN students s1
            ON relations.student1_id = s1.id
        JOIN students s2
            ON relations.student2_id = s2.id
        ORDER BY relations.id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "relations.html",
        students=students,
        relations=relations
    )


@app.route("/add_relation", methods=["POST"])
def add_relation():

    student1_id = request.form["student1"]
    student2_id = request.form["student2"]
    relation_type = request.form["relation_type"]

    if student1_id == student2_id:
        return redirect(url_for("relations"))

    conn = get_db_connection()

    conn.execute("""
        INSERT INTO relations
        (student1_id, student2_id, relation_type)
        VALUES (?, ?, ?)
    """, (
        student1_id,
        student2_id,
        relation_type
    ))

    conn.commit()
    conn.close()

    return redirect(url_for("relations"))


@app.route("/delete_relation/<int:relation_id>")
def delete_relation(relation_id):

    conn = get_db_connection()

    conn.execute(
        "DELETE FROM relations WHERE id = ?",
        (relation_id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("relations"))


# =========================
# ANALYSIS
# =========================

@app.route("/analysis")
def analysis():

    conn = get_db_connection()

    students = conn.execute(
        "SELECT * FROM students ORDER BY name"
    ).fetchall()

    relation_types = conn.execute("""
        SELECT DISTINCT relation_type
        FROM relations
        ORDER BY relation_type
    """).fetchall()

    conn.close()

    return render_template(
        "analysis.html",
        students=students,
        relation_types=relation_types
    )


@app.route("/analyze_relation", methods=["POST"])
def analyze_relation():

    relation_type = request.form["relation_type"]

    conn = get_db_connection()

    students = conn.execute(
        "SELECT * FROM students ORDER BY name"
    ).fetchall()

    relation_rows = conn.execute("""
        SELECT student1_id, student2_id
        FROM relations
        WHERE relation_type = ?
    """, (relation_type,)).fetchall()

    relation_types = conn.execute("""
        SELECT DISTINCT relation_type
        FROM relations
        ORDER BY relation_type
    """).fetchall()

    conn.close()

    relation = set()

    for row in relation_rows:

        relation.add(
            (row["student1_id"], row["student2_id"])
        )


    student_ids = {
        student["id"]
        for student in students
    }


    # Reflexive

    reflexive = all(
        (student_id, student_id) in relation
        for student_id in student_ids
    )


    # Symmetric

    symmetric = all(
        (b, a) in relation
        for a, b in relation
    )


    # Antisymmetric

    antisymmetric = all(
        a == b or (b, a) not in relation
        for a, b in relation
    )


    # Transitive

    transitive = True

    for a, b in relation:

        for x, c in relation:

            if b == x and (a, c) not in relation:

                transitive = False
                break

        if not transitive:
            break


    # Equivalence Relation

    equivalence = (
        reflexive
        and symmetric
        and transitive
    )


    # Partial Order

    partial_order = (
        reflexive
        and antisymmetric
        and transitive
    )


    # Relation Matrix

    matrix = []

    for student1 in students:

        row = []

        for student2 in students:

            if (
                student1["id"],
                student2["id"]
            ) in relation:

                row.append(1)

            else:

                row.append(0)

        matrix.append(row)


    return render_template(
        "analysis.html",

        students=students,

        relation_types=relation_types,

        selected_relation=relation_type,

        relation_count=len(relation),

        reflexive=reflexive,
        symmetric=symmetric,
        antisymmetric=antisymmetric,
        transitive=transitive,

        equivalence=equivalence,
        partial_order=partial_order,

        matrix=matrix
    )


# =========================
# RUN APPLICATION
# =========================

if __name__ == "__main__":
    app.run(debug=True)