import json
import hashlib
from datetime import datetime
import os
import streamlit as st

# ============================================================
# 🗄️ VERİTABANI BAĞLANTI YÖNETİMİ
# ============================================================
# PERFORMANS: Bağlantı pooling ile her çağrıda yeni TCP/SSL
# bağlantısı açılmaz. Tek bağlantı @st.cache_resource ile
# tüm rerun'lar boyunca canlı tutulur.
# ============================================================

try:
    import psycopg2
    import psycopg2.extras
    DB_ENGINE = "postgresql"
except ImportError:
    DB_ENGINE = "sqlite"
    import sqlite3

# SQLite fallback DB adı
SQLITE_DB_NAME = "school_data.db"

# init_db tekrar çağrılmasını önleyen bayrak
_db_initialized = False


def get_db_url():
    """
    Supabase PostgreSQL bağlantı URL'sini alır.
    Öncelik: st.secrets → ortam değişkeni
    Bulunamazsa None döner (SQLite fallback).
    """
    try:
        if "SUPABASE_DB_URL" in st.secrets:
            return st.secrets["SUPABASE_DB_URL"]
    except Exception:
        pass

    env_url = os.getenv("SUPABASE_DB_URL")
    if env_url:
        return env_url

    return None


# ============================================================
# BAĞLANTI POOLING — @st.cache_resource
# ============================================================
# Streamlit her butona basışta tüm script'i yeniden çalıştırır.
# @st.cache_resource ile PostgreSQL bağlantısı SADECE İLK SEFERDE
# açılır ve tüm rerun'lar boyunca yeniden kullanılır.
# Bu ~300-500ms tasarruf sağlar (DNS + TCP + SSL + PG auth).
# ============================================================

class _PgConnWrapper:
    """
    PostgreSQL cached connection wrapper.
    close() gerçekten kapatmaz — sadece rollback yapar.
    Böylece mevcut tüm kod değişmeden çalışır.
    """
    def __init__(self, real_conn):
        self._conn = real_conn

    def cursor(self):
        return self._conn.cursor()

    def commit(self):
        self._conn.commit()

    def rollback(self):
        try:
            self._conn.rollback()
        except Exception:
            pass

    def close(self):
        # Kapatma! Sadece temizle.
        try:
            self._conn.rollback()
        except Exception:
            pass

    @property
    def autocommit(self):
        return self._conn.autocommit

    @autocommit.setter
    def autocommit(self, val):
        self._conn.autocommit = val


@st.cache_resource
def _get_cached_pg_conn():
    """Cached PostgreSQL bağlantısı — rerun'lar arası yaşar."""
    db_url = get_db_url()
    if db_url and DB_ENGINE == "postgresql":
        try:
            conn = psycopg2.connect(db_url, connect_timeout=10)
            return conn
        except Exception as e:
            print(f"PostgreSQL bağlantı hatası: {e}")
    return None


def _check_pg_conn(conn):
    """Bağlantı hala canlı mı kontrol et."""
    try:
        conn.cursor().execute("SELECT 1")
        conn.rollback()
        return True
    except Exception:
        return False


def get_connection():
    """
    Veritabanı bağlantısı döndürür.
    PostgreSQL: Cached bağlantı (hızlı — yeni TCP açmaz)
    SQLite: Her seferinde yeni bağlantı (lokal, zaten hızlı)
    """
    if DB_ENGINE == "postgresql":
        raw_conn = _get_cached_pg_conn()
        if raw_conn is not None:
            if _check_pg_conn(raw_conn):
                raw_conn.autocommit = False
                return _PgConnWrapper(raw_conn), "postgresql"
            else:
                # Bağlantı kopmuş — cache'i temizle, yeniden bağlan
                _get_cached_pg_conn.clear()
                raw_conn = _get_cached_pg_conn()
                if raw_conn is not None:
                    raw_conn.autocommit = False
                    return _PgConnWrapper(raw_conn), "postgresql"

    # SQLite Fallback
    try:
        conn = sqlite3.connect(SQLITE_DB_NAME)
        return conn, "sqlite"
    except NameError:
        import sqlite3 as sq3
        conn = sq3.connect(SQLITE_DB_NAME)
        return conn, "sqlite"


def is_using_sqlite():
    """Veritabanı SQLite mi kullanıyor? (Kalıcılık uyarısı için)"""
    return get_db_url() is None


def get_placeholder(engine):
    """SQL placeholder: PostgreSQL=%s, SQLite=?"""
    return "%s" if engine == "postgresql" else "?"


# ============================================================
# SINIF TANIMLAMALARI
# ============================================================

class Student:
    """login_student fonksiyonunun döndürdüğü öğrenci nesnesi."""
    def __init__(self, data, login_count):
        self.id          = data[0]
        self.name        = data[1]
        self.username    = data[2]
        self.password    = data[3]
        self.age         = data[4]
        self.gender      = data[5]
        self.grade       = data[6]  # Sınıf numarası (5-12)
        self.login_count = login_count


class StudentInfo:
    """get_all_students_with_results fonksiyonunun döndürdüğü öğrenci nesnesi."""
    def __init__(self, data):
        self.id          = data[0]
        self.name        = data[1]
        self.username    = data[2]
        self.password    = data[3]
        self.age         = data[4]
        self.gender      = data[5]
        self.grade       = data[6]  # Sınıf numarası (5-12)
        self.login_count = data[7]


# ============================================================
# ŞİFRE YARDIMCI FONKSİYONU
# ============================================================

def hash_password(password: str) -> str:
    """SHA-256 ile şifre hash'ler."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


# ============================================================
# VERİTABANI BAŞLATMA
# ============================================================

def init_db():
    """
    Veritabanı tablolarını oluşturur.
    PostgreSQL ve SQLite uyumlu.
    PERFORMANS: Sadece ilk çağrıda çalışır, sonraki çağrılar atlanır.
    """
    global _db_initialized
    if _db_initialized:
        return
    
    conn, engine = get_connection()
    c = conn.cursor()

    try:
        if engine == "postgresql":
            # --- PostgreSQL Tabloları ---
            c.execute('''CREATE TABLE IF NOT EXISTS teachers (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                password TEXT NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT NOW()
            )''')

            c.execute('''CREATE TABLE IF NOT EXISTS students (
                id SERIAL PRIMARY KEY,
                name TEXT,
                username TEXT UNIQUE,
                password TEXT,
                age INTEGER,
                gender TEXT,
                grade TEXT,
                login_count INTEGER DEFAULT 0,
                secret_word TEXT,
                teacher_id INTEGER REFERENCES teachers(id) ON DELETE SET NULL
            )''')

            # Migration: mevcut tablolara yeni sütunlar
            for migration_sql in [
                "ALTER TABLE students ADD COLUMN grade TEXT",
                "ALTER TABLE students ADD COLUMN teacher_id INTEGER REFERENCES teachers(id) ON DELETE SET NULL",
            ]:
                try:
                    c.execute(migration_sql)
                except Exception:
                    pass

            c.execute('''CREATE TABLE IF NOT EXISTS results (
                id SERIAL PRIMARY KEY,
                student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
                test_name TEXT,
                raw_answers TEXT,
                scores TEXT,
                report TEXT,
                date TIMESTAMP DEFAULT NOW()
            )''')

            c.execute('''CREATE TABLE IF NOT EXISTS analysis_history (
                id SERIAL PRIMARY KEY,
                student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
                combination TEXT,
                ai_report TEXT,
                date TIMESTAMP DEFAULT NOW()
            )''')

            c.execute('''CREATE INDEX IF NOT EXISTS idx_results_student_test 
                         ON results(student_id, test_name)''')

        else:
            # --- SQLite Tabloları ---
            c.execute('''CREATE TABLE IF NOT EXISTS teachers
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          name TEXT NOT NULL,
                          password TEXT NOT NULL,
                          is_active INTEGER DEFAULT 1,
                          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

            c.execute('''CREATE TABLE IF NOT EXISTS students
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          name TEXT, username TEXT, password TEXT,
                          age INTEGER, gender TEXT, grade TEXT,
                          login_count INTEGER DEFAULT 0,
                          secret_word TEXT,
                          teacher_id INTEGER)''')

            for mig in [
                "ALTER TABLE students ADD COLUMN secret_word TEXT",
                "ALTER TABLE students ADD COLUMN grade TEXT",
                "ALTER TABLE students ADD COLUMN teacher_id INTEGER",
            ]:
                try:
                    c.execute(mig)
                except Exception:
                    pass

            c.execute('''CREATE TABLE IF NOT EXISTS results
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          student_id INTEGER,
                          test_name TEXT,
                          raw_answers TEXT,
                          scores TEXT,
                          report TEXT,
                          date TIMESTAMP)''')

            c.execute('''CREATE TABLE IF NOT EXISTS analysis_history
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          student_id INTEGER,
                          combination TEXT,
                          ai_report TEXT,
                          date TIMESTAMP)''')

        conn.commit()
        _db_initialized = True
    except Exception as e:
        conn.rollback()
        print(f"init_db hatası: {e}")
    finally:
        conn.close()


# ============================================================
# ÖĞRENCİ KİMLİK / KAYIT İŞLEMLERİ
# ============================================================

def register_student(name, username, password, age, gender, secret_word="", grade=None):
    """Yeni öğrenci kaydeder."""
    conn, engine = get_connection()
    c = conn.cursor()
    ph = get_placeholder(engine)

    try:
        c.execute(f"SELECT id FROM students WHERE username={ph}", (username,))
        if c.fetchone():
            return False, "Bu e-posta adresi zaten kayıtlı."

        hashed_pw = hash_password(password)
        hashed_secret = hash_password(secret_word) if secret_word else ""
        c.execute(
            f"INSERT INTO students (name, username, password, age, gender, grade, secret_word) VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph})",
            (name, username, hashed_pw, age, gender, grade, hashed_secret)
        )
        conn.commit()
        return True, "Kayıt Başarılı"

    except Exception as e:
        conn.rollback()
        return False, f"Kayıt sırasında hata: {e}"

    finally:
        conn.close()


def login_student(username, password):
    """Öğrenci girişi doğrular."""
    conn, engine = get_connection()
    c = conn.cursor()
    ph = get_placeholder(engine)

    try:
        hashed_pw = hash_password(password)

        c.execute(
            f"SELECT id, name, username, password, age, gender, grade, login_count FROM students WHERE username={ph} AND password={ph}",
            (username, hashed_pw)
        )
        user = c.fetchone()

        if user:
            new_count = (user[7] or 0) + 1
            c.execute(f"UPDATE students SET login_count={ph} WHERE id={ph}", (new_count, user[0]))
            conn.commit()
            return True, Student(user, new_count)

        return False, None

    except Exception as e:
        conn.rollback()
        print(f"Login hatası: {e}")
        return False, None

    finally:
        conn.close()


def reset_student_password(username, secret_word, new_password):
    """Öğrenci şifresini sıfırlar."""
    conn, engine = get_connection()
    c = conn.cursor()
    ph = get_placeholder(engine)

    try:
        c.execute(f"SELECT id, secret_word FROM students WHERE username={ph}", (username,))
        user_data = c.fetchone()

        if not user_data:
            return False, "Sistemde böyle bir e-posta adresi bulunamadı."

        user_id = user_data[0]
        stored_secret = user_data[1]

        if not stored_secret:
            return False, "Bu hesaba ait kurtarma kelimesi bulunmuyor (Eski kayıt olabilir). Lütfen yeni hesap açın."

        # Hash'li karşılaştırma (yeni kayıtlar)
        hashed_input = hash_password(secret_word.lower().strip())
        if stored_secret == hashed_input:
            pass  # Eşleşti — devam et
        elif stored_secret.lower().strip() == secret_word.lower().strip():
            # Eski kayıt (düz metin) — eşleşti, hash'e yükselt
            c.execute(f"UPDATE students SET secret_word={ph} WHERE id={ph}", (hashed_input, user_id))
        else:
            return False, "Girilen kurtarma kelimesi yanlış!"

        new_hashed_pw = hash_password(new_password)
        c.execute(f"UPDATE students SET password={ph} WHERE id={ph}", (new_hashed_pw, user_id))
        conn.commit()

        return True, "Şifreniz başarıyla yenilendi."

    except Exception as e:
        conn.rollback()
        return False, f"Şifre sıfırlama hatası: {e}"

    finally:
        conn.close()


# ============================================================
# TEST KAYIT İŞLEMLERİ
# ============================================================

def save_test_result_to_db(student_id, test_name, raw_answers, scores, report_text):
    """Test sonucunu veritabanına kaydeder. Varsa eski kaydı günceller."""
    conn, engine = get_connection()
    c = conn.cursor()
    ph = get_placeholder(engine)

    try:
        c.execute(
            f"DELETE FROM results WHERE student_id={ph} AND test_name={ph}",
            (student_id, test_name)
        )

        c.execute(
            f"INSERT INTO results (student_id, test_name, raw_answers, scores, report, date) VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph})",
            (
                student_id,
                test_name,
                json.dumps(raw_answers, ensure_ascii=False),
                json.dumps(scores, ensure_ascii=False),
                report_text,
                datetime.now()
            )
        )
        conn.commit()
        return True

    except Exception as e:
        conn.rollback()
        print(f"Test kayıt hatası: {e}")
        return False

    finally:
        conn.close()


def check_test_completed(student_id, test_name):
    """Öğrencinin belirli bir testi tamamlayıp tamamlamadığını kontrol eder."""
    conn, engine = get_connection()
    c = conn.cursor()
    ph = get_placeholder(engine)

    try:
        c.execute(
            f"SELECT id FROM results WHERE student_id={ph} AND test_name={ph}",
            (student_id, test_name)
        )
        data = c.fetchone()
        return data is not None
    except Exception:
        return False
    finally:
        conn.close()


def get_completed_tests(student_id):
    """
    Öğrencinin tamamladığı tüm test adlarını döndürür.
    PERFORMANS: Tek sorgu ile 9 ayrı check_test_completed çağrısını değiştirir.
    """
    conn, engine = get_connection()
    c = conn.cursor()
    ph = get_placeholder(engine)

    try:
        c.execute(
            f"SELECT DISTINCT test_name FROM results WHERE student_id={ph}",
            (student_id,)
        )
        return {row[0] for row in c.fetchall()}
    except Exception:
        return set()
    finally:
        conn.close()


# ============================================================
# ÖĞRETMEN VERİ ÇEKME İŞLEMLERİ
# ============================================================

def get_all_students_with_results():
    """Tüm öğrencileri ve test sonuçlarını döndürür."""
    conn, engine = get_connection()
    c = conn.cursor()
    ph = get_placeholder(engine)

    try:
        c.execute("SELECT id, name, username, password, age, gender, grade, login_count FROM students ORDER BY name")
        students_raw = c.fetchall()

        all_data = []
        for s in students_raw:
            c.execute(
                f"SELECT test_name, scores, raw_answers, date, report FROM results WHERE student_id={ph} ORDER BY date DESC",
                (s[0],)
            )
            tests_raw = c.fetchall()

            tests_list = []
            for t in tests_raw:
                try:
                    score_json = json.loads(t[1]) if t[1] else {}
                except (json.JSONDecodeError, TypeError):
                    score_json = {}

                tests_list.append({
                    "test_name": t[0],
                    "scores": score_json,
                    "raw_answers": t[2],
                    "date": str(t[3]) if t[3] else "",
                    "report": t[4]
                })

            all_data.append({
                "info": StudentInfo(s),
                "tests": tests_list
            })

        return all_data

    except Exception as e:
        print(f"⚠️ get_all_students_with_results hatası: {e}")
        try:
            conn.rollback()
        except Exception:
            pass
        try:
            st.session_state["_last_db_error"] = f"get_all_students_with_results: {str(e)[:200]}"
        except Exception:
            pass
        return []

    finally:
        conn.close()


def get_student_analysis_history(student_id):
    """Öğrencinin AI analiz arşivini döndürür."""
    conn, engine = get_connection()
    c = conn.cursor()
    ph = get_placeholder(engine)

    try:
        c.execute(
            f"SELECT combination, ai_report, date FROM analysis_history WHERE student_id={ph} ORDER BY date DESC",
            (student_id,)
        )
        rows = c.fetchall()

        history = []
        for r in rows:
            history.append({
                "combination": r[0],
                "report": r[1],
                "date": str(r[2]) if r[2] else ""
            })
        return history

    except Exception:
        return []

    finally:
        conn.close()


def save_holistic_analysis(student_id, combination_list, report_text):
    """AI analiz raporunu arşive kaydeder."""
    conn, engine = get_connection()
    c = conn.cursor()
    ph = get_placeholder(engine)
    comb_str = " + ".join(combination_list)

    try:
        c.execute(
            f"INSERT INTO analysis_history (student_id, combination, ai_report, date) VALUES ({ph}, {ph}, {ph}, {ph})",
            (student_id, comb_str, report_text, datetime.now())
        )
        conn.commit()

    except Exception as e:
        conn.rollback()
        print(f"Analiz kayıt hatası: {e}")

    finally:
        conn.close()


def delete_specific_students(names_list):
    """Belirtilen öğrencilerin tüm verilerini siler."""
    conn, engine = get_connection()
    c = conn.cursor()
    ph = get_placeholder(engine)

    try:
        for name in names_list:
            c.execute(f"SELECT id FROM students WHERE name={ph}", (name,))
            sid = c.fetchone()
            if sid:
                c.execute(f"DELETE FROM analysis_history WHERE student_id={ph}", (sid[0],))
                c.execute(f"DELETE FROM results WHERE student_id={ph}", (sid[0],))
                c.execute(f"DELETE FROM students WHERE id={ph}", (sid[0],))
        conn.commit()
        return True

    except Exception as e:
        conn.rollback()
        print(f"Silme hatası: {e}")
        return False

    finally:
        conn.close()


def reset_database():
    """
    Tüm veritabanını sıfırlar.
    PostgreSQL: Tabloları DROP eder ve yeniden oluşturur.
    SQLite: Dosyayı siler ve yeniden oluşturur.
    """
    global _db_initialized
    conn, engine = get_connection()
    c = conn.cursor()

    try:
        if engine == "postgresql":
            c.execute("DROP TABLE IF EXISTS analysis_history CASCADE")
            c.execute("DROP TABLE IF EXISTS results CASCADE")
            c.execute("DROP TABLE IF EXISTS students CASCADE")
            conn.commit()
        else:
            conn.close()
            conn = None
            if os.path.exists(SQLITE_DB_NAME):
                os.remove(SQLITE_DB_NAME)

        _db_initialized = False
        init_db()
        return True

    except Exception as e:
        if conn:
            try:
                conn.rollback()
            except Exception:
                pass
        print(f"Sıfırlama hatası: {e}")
        return False

    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass


def repair_database():
    """
    Veritabanını onarmaya çalışır.
    Eksik tabloları yeniden oluşturur (varsa dokunmaz).
    """
    global _db_initialized
    try:
        _db_initialized = False
        init_db()
        return True
    except Exception:
        return False


# ============================================================
# GRADE (SINIF) YARDIMCI FONKSİYONU
# ============================================================

def format_grade(grade_val):
    """Grade değerini görüntüleme metnine çevirir."""
    if grade_val is None:
        return "Belirtilmemiş"
    g = str(grade_val).strip()
    if g.lower() == "mezun" or g == "0":
        return "Mezun"
    try:
        return f"{int(g)}. Sınıf"
    except (ValueError, TypeError):
        return g if g else "Belirtilmemiş"


# ============================================================
# ÖĞRETMEN YÖNETİM FONKSİYONLARI
# ============================================================

def create_teacher(name, password):
    """Yeni öğretmen oluşturur."""
    conn, engine = get_connection()
    c = conn.cursor()
    ph = get_placeholder(engine)
    try:
        hashed_pw = hash_password(password)
        c.execute(f"INSERT INTO teachers (name, password) VALUES ({ph}, {ph})", (name, hashed_pw))
        conn.commit()
        return True, "Öğretmen başarıyla oluşturuldu."
    except Exception as e:
        conn.rollback()
        return False, f"Hata: {e}"
    finally:
        conn.close()


def authenticate_teacher(teacher_id, password):
    """Öğretmen şifresini doğrular."""
    conn, engine = get_connection()
    c = conn.cursor()
    ph = get_placeholder(engine)
    try:
        hashed_pw = hash_password(password)
        active_val = True if engine == "postgresql" else 1
        c.execute(
            f"SELECT id, name FROM teachers WHERE id={ph} AND password={ph} AND is_active={ph}",
            (teacher_id, hashed_pw, active_val)
        )
        row = c.fetchone()
        if row:
            return True, {"id": row[0], "name": row[1]}
        return False, None
    except Exception:
        return False, None
    finally:
        conn.close()


def get_all_teachers():
    """Tüm aktif öğretmenleri döndürür."""
    conn, engine = get_connection()
    c = conn.cursor()
    try:
        active_val = True if engine == "postgresql" else 1
        ph = get_placeholder(engine)
        c.execute(f"SELECT id, name, created_at FROM teachers WHERE is_active={ph} ORDER BY name", (active_val,))
        rows = c.fetchall()
        return [{"id": r[0], "name": r[1], "created_at": str(r[2]) if r[2] else ""} for r in rows]
    except Exception as e:
        print(f"⚠️ get_all_teachers hatası: {e}")
        try:
            conn.rollback()
        except Exception:
            pass
        # Session state'e kaydet ki UI görebilsin
        try:
            st.session_state["_last_db_error"] = f"get_all_teachers: {str(e)[:200]}"
        except Exception:
            pass
        return []
    finally:
        conn.close()


def update_teacher_password(teacher_id, new_password):
    """Öğretmen şifresini günceller."""
    conn, engine = get_connection()
    c = conn.cursor()
    ph = get_placeholder(engine)
    try:
        hashed_pw = hash_password(new_password)
        c.execute(f"UPDATE teachers SET password={ph} WHERE id={ph}", (hashed_pw, teacher_id))
        conn.commit()
        return True
    except Exception:
        conn.rollback()
        return False
    finally:
        conn.close()


def delete_teacher(teacher_id):
    """Öğretmeni pasif yapar (soft delete)."""
    conn, engine = get_connection()
    c = conn.cursor()
    ph = get_placeholder(engine)
    try:
        inactive_val = False if engine == "postgresql" else 0
        c.execute(f"UPDATE teachers SET is_active={ph} WHERE id={ph}", (inactive_val, teacher_id))
        # Öğretmene bağlı öğrencilerin teacher_id'sini temizle
        c.execute(f"UPDATE students SET teacher_id=NULL WHERE teacher_id={ph}", (teacher_id,))
        conn.commit()
        return True
    except Exception:
        conn.rollback()
        return False
    finally:
        conn.close()


def assign_student_to_teacher(student_id, teacher_id):
    """Öğrenciyi bir öğretmene atar."""
    conn, engine = get_connection()
    c = conn.cursor()
    ph = get_placeholder(engine)
    try:
        c.execute(f"UPDATE students SET teacher_id={ph} WHERE id={ph}", (teacher_id, student_id))
        conn.commit()
        return True
    except Exception:
        conn.rollback()
        return False
    finally:
        conn.close()


def get_students_by_teacher(teacher_id):
    """Belirli bir öğretmene atanmış öğrencileri ve test sonuçlarını döndürür."""
    conn, engine = get_connection()
    c = conn.cursor()
    ph = get_placeholder(engine)
    try:
        c.execute(
            f"SELECT id, name, username, password, age, gender, grade, login_count FROM students WHERE teacher_id={ph} ORDER BY name",
            (teacher_id,)
        )
        students_raw = c.fetchall()

        all_data = []
        for s in students_raw:
            c.execute(
                f"SELECT test_name, scores, raw_answers, date, report FROM results WHERE student_id={ph} ORDER BY date DESC",
                (s[0],)
            )
            tests_raw = c.fetchall()
            tests_list = []
            for t in tests_raw:
                try:
                    score_json = json.loads(t[1]) if t[1] else {}
                except (json.JSONDecodeError, TypeError):
                    score_json = {}
                tests_list.append({
                    "test_name": t[0],
                    "scores": score_json,
                    "raw_answers": t[2],
                    "date": str(t[3]) if t[3] else "",
                    "report": t[4]
                })
            all_data.append({
                "info": StudentInfo(s),
                "tests": tests_list
            })
        return all_data
    except Exception as e:
        print(f"get_students_by_teacher hatası: {e}")
        return []
    finally:
        conn.close()


def get_unassigned_students():
    """Herhangi bir öğretmene atanmamış öğrencileri döndürür."""
    conn, engine = get_connection()
    c = conn.cursor()
    try:
        c.execute("SELECT id, name FROM students WHERE teacher_id IS NULL ORDER BY name")
        return [{"id": r[0], "name": r[1]} for r in c.fetchall()]
    except Exception:
        return []
    finally:
        conn.close()


# ============================================================
# 🩺 SİSTEM SAĞLIĞI / DIAGNOSTIC
# ============================================================

def get_db_diagnostics():
    """
    Veritabanı ve secret durumunu kapsamlı şekilde döndürür.
    Sorun teşhisi için.
    """
    info = {
        "db_engine": None,
        "db_url_present": False,
        "teacher_password_configured": False,
        "anthropic_key_configured": False,
        "connection_ok": False,
        "connection_error": None,
        "teachers_count": None,
        "teachers_error": None,
        "students_count": None,
        "students_error": None,
        "results_count": None,
        "results_error": None,
        "active_teachers_count": None,
        "tables_exist": {},
    }

    # Secrets kontrolü
    try:
        if "SUPABASE_DB_URL" in st.secrets and st.secrets["SUPABASE_DB_URL"]:
            info["db_url_present"] = True
    except Exception:
        pass
    if not info["db_url_present"] and os.getenv("SUPABASE_DB_URL"):
        info["db_url_present"] = True

    try:
        if "teacher_password" in st.secrets and st.secrets["teacher_password"]:
            info["teacher_password_configured"] = True
    except Exception:
        pass
    if not info["teacher_password_configured"] and os.getenv("TEACHER_PASSWORD"):
        info["teacher_password_configured"] = True

    try:
        if "ANTHROPIC_API_KEY" in st.secrets and st.secrets["ANTHROPIC_API_KEY"]:
            info["anthropic_key_configured"] = True
    except Exception:
        pass
    if not info["anthropic_key_configured"] and os.getenv("ANTHROPIC_API_KEY"):
        info["anthropic_key_configured"] = True

    # DB bağlantısı
    try:
        conn, engine = get_connection()
        info["db_engine"] = engine
        info["connection_ok"] = True
        c = conn.cursor()

        # Hangi tablolar var?
        for tbl in ["teachers", "students", "results", "analysis_history"]:
            try:
                c.execute(f"SELECT COUNT(*) FROM {tbl}")
                cnt = c.fetchone()
                info["tables_exist"][tbl] = cnt[0] if cnt else 0
            except Exception as e:
                info["tables_exist"][tbl] = f"HATA: {str(e)[:100]}"
                try:
                    conn.rollback()
                except Exception:
                    pass

        # teachers detay
        try:
            c.execute("SELECT COUNT(*) FROM teachers")
            row = c.fetchone()
            info["teachers_count"] = row[0] if row else 0
        except Exception as e:
            info["teachers_error"] = str(e)[:200]
            try:
                conn.rollback()
            except Exception:
                pass

        try:
            ph = get_placeholder(engine)
            active_val = True if engine == "postgresql" else 1
            c.execute(f"SELECT COUNT(*) FROM teachers WHERE is_active={ph}", (active_val,))
            row = c.fetchone()
            info["active_teachers_count"] = row[0] if row else 0
        except Exception as e:
            try:
                conn.rollback()
            except Exception:
                pass

        # students detay
        try:
            c.execute("SELECT COUNT(*) FROM students")
            row = c.fetchone()
            info["students_count"] = row[0] if row else 0
        except Exception as e:
            info["students_error"] = str(e)[:200]
            try:
                conn.rollback()
            except Exception:
                pass

        # results detay
        try:
            c.execute("SELECT COUNT(*) FROM results")
            row = c.fetchone()
            info["results_count"] = row[0] if row else 0
        except Exception as e:
            info["results_error"] = str(e)[:200]
            try:
                conn.rollback()
            except Exception:
                pass

        conn.close()

    except Exception as e:
        info["connection_error"] = str(e)[:300]

    return info


def bootstrap_first_teacher(name, password):
    """
    Teachers tablosu boşken ilk öğretmeni doğrudan oluşturur.
    Güvenlik: sadece tablo boşsa çalışır.
    """
    conn, engine = get_connection()
    c = conn.cursor()
    ph = get_placeholder(engine)
    try:
        c.execute("SELECT COUNT(*) FROM teachers")
        row = c.fetchone()
        count = row[0] if row else 0
        if count > 0:
            return False, f"Teachers tablosunda {count} kayıt zaten var. Bootstrap sadece boş tablolarda çalışır."

        hashed_pw = hash_password(password)
        active_val = True if engine == "postgresql" else 1
        c.execute(
            f"INSERT INTO teachers (name, password, is_active) VALUES ({ph}, {ph}, {ph})",
            (name, hashed_pw, active_val)
        )
        conn.commit()
        return True, f"✅ İlk öğretmen '{name}' başarıyla oluşturuldu."
    except Exception as e:
        try:
            conn.rollback()
        except Exception:
            pass
        return False, f"Hata: {str(e)[:200]}"
    finally:
        conn.close()
