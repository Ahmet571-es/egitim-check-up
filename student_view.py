import streamlit as st
import streamlit.components.v1 as components
import json
import time
import random
from db_utils import check_test_completed, save_test_result_to_db, get_completed_tests
from p2_engine import (
    P2_CONFIG, generate_p2_test, generate_practice_row as p2_generate_practice_row,
    calculate_p2, generate_p2_report,
    get_time_per_row as p2_get_time_per_row,
    P2_CSS, render_symbol_label as p2_render_symbol_label,
    render_instructions_html as p2_render_instructions_html,
    render_practice_instructions_html as p2_render_practice_instructions_html,
    render_full_analysis_html as p2_render_full_analysis_html,
    render_target_examples as p2_render_target_examples,
)
from akademik_engine import (
    get_akademik_sections, get_total_questions,
    calculate_akademik, generate_akademik_report,
)
from hizli_okuma_engine import (
    get_passage_for_grade, count_words,
    calculate_speed_reading, generate_speed_reading_report,
)

# --- TEST VERİLERİ MODÜLÜ ---
from test_data import (
    # Sağ-Sol Beyin
    SAG_SOL_BEYIN_QUESTIONS, SAG_SOL_BEYIN_DATA,
    calculate_sag_sol_beyin,
    # Çalışma Davranışı
    CALISMA_DAVRANISI_QUESTIONS, CALISMA_DAVRANISI_CATEGORIES,
    calculate_calisma_davranisi,
    # Sınav Kaygısı
    SINAV_KAYGISI_QUESTIONS, SINAV_KAYGISI_CATEGORIES,
    calculate_sinav_kaygisi,
    # Çoklu Zeka
    COKLU_ZEKA_QUESTIONS_LISE, COKLU_ZEKA_QUESTIONS_ILKOGRETIM,
    COKLU_ZEKA_DATA, ZEKA_SIRA,
    calculate_coklu_zeka_lise, calculate_coklu_zeka_ilkogretim,
    # VARK
    VARK_QUESTIONS, VARK_SCORING, VARK_STYLES,
    calculate_vark,
    # Holland RIASEC
    HOLLAND_QUESTIONS, HOLLAND_TYPES,
    calculate_holland,
    # Enneagram
    ENNEAGRAM_QUESTIONS, ENNEAGRAM_DATA, WING_DESCRIPTIONS,
    calculate_enneagram_report,
)


# ============================================================
# TEST META BİLGİLERİ (YENİ — Süre + Açıklama + İkon)
# ============================================================
TEST_META = {
    "Enneagram Kişilik Testi": {
        "icon": "🧬",
        "color": "#8E44AD",
        "duration": "~25 dk",
        "questions": 180,
        "desc": "9 kişilik tipinden hangisine en yakınsın? Güçlü yönlerini, korkularını ve büyüme yolunu keşfet.",
    },
    "Çalışma Davranışı Ölçeği": {
        "icon": "📚",
        "color": "#2E86C1",
        "duration": "~15 dk",
        "questions": 73,
        "desc": "Ders çalışma alışkanlıklarını ve akademik davranış kalıplarını analiz et.",
    },
    "Sağ-Sol Beyin Dominansı Testi": {
        "icon": "🧠",
        "color": "#E74C3C",
        "duration": "~7 dk",
        "questions": 30,
        "desc": "Beyinin hangi yarısı daha baskın? Yaratıcı mı, analitik mi, yoksa dengeli misin?",
    },
    "Sınav Kaygısı Ölçeği": {
        "icon": "😰",
        "color": "#F39C12",
        "duration": "~10 dk",
        "questions": 50,
        "desc": "Sınav kaygın hangi boyutlarda seni etkiliyor? Fiziksel, zihinsel, duygusal...",
    },
    "VARK Öğrenme Stilleri Testi": {
        "icon": "👁️",
        "color": "#27AE60",
        "duration": "~8 dk",
        "questions": 16,
        "desc": "En iyi nasıl öğreniyorsun? Görsel, İşitsel, Okuma/Yazma, Kinestetik...",
    },
    "Çoklu Zeka Testi": {
        "icon": "💡",
        "color": "#3498DB",
        "duration": "~12 dk",
        "questions": 80,
        "desc": "Howard Gardner'ın 8 zeka alanından hangilerinde güçlüsün?",
    },
    "Holland Mesleki İlgi Envanteri": {
        "icon": "🧭",
        "color": "#1ABC9C",
        "duration": "~15 dk",
        "questions": 84,
        "desc": "Hangi meslek alanları sana en uygun? RIASEC koduyla kariyer haritanı çıkar.",
    },
    "P2 Dikkat Testi": {
        "icon": "👁️",
        "color": "#2980B9",
        "duration": "~7 dk",
        "questions": 450,
        "desc": "Seçici dikkat ve konsantrasyon ölçümü. 'p' harfi hedefli, nokta bazlı zamanlı test.",
    },
    "Akademik Analiz Testi": {
        "icon": "📚",
        "color": "#9B59B6",
        "duration": "~25 dk",
        "questions": 67,
        "desc": "Okuma anlama, matematik, mantık ve akademik öz-değerlendirme ile akademik profilini çıkar.",
    },
    "Hızlı Okuma Testi": {
        "icon": "📖",
        "color": "#E67E22",
        "duration": "~5 dk",
        "questions": 10,
        "desc": "Okuma hızını (kelime/dakika) ölç ve okuduğunu ne kadar anladığını test et.",
    },
}


# ============================================================
# 🏠 ANA APP FONKSİYONU
# ============================================================

# ============================================================
# 🚀 PERFORMANS: Test soru bölümü @st.fragment ile izole
#    Butona basınca sadece bu kısım yenilenir, tüm sayfa değil
# ============================================================
@st.fragment
def _render_test_questions():
    """Test soru arayüzü — fragment olarak sadece kendi kendini yeniler."""
    t_name = st.session_state.selected_test

    # ── Fragment içi scroll (fragment rerun'larında app() sonu çalışmaz)
    if st.session_state.get("_scroll_top"):
        st.session_state._scroll_top = False
        components.html(
            """<script>
            (function(){
                function doScroll(){
                    try{
                        var m = window.parent.document.querySelector('section.main');
                        if(m) m.scrollTo({top:0, behavior:'instant'});
                        var c = window.parent.document.querySelector('[data-testid="stAppViewContainer"]');
                        if(c) c.scrollTo({top:0, behavior:'instant'});
                        window.parent.scrollTo(0,0);
                    }catch(e){}
                }
                doScroll();
                setTimeout(doScroll, 150);
                setTimeout(doScroll, 400);
                setTimeout(doScroll, 800);
            })();
            </script>""", height=0,
        )

    data = st.session_state.current_test_data
    q_type = data.get("type")

    # ========================================
    # TİP: ENNEAGRAM — KARISIK SAYFALANMIŞ
    # ========================================
    if q_type == "enneagram_fixed":
        PER_PAGE  = 20
        all_qs    = st.session_state.enneagram_shuffled
        total_qs  = len(all_qs)
        curr_page = st.session_state.enneagram_page
        total_pages = (total_qs + PER_PAGE - 1) // PER_PAGE

        page_qs  = all_qs[curr_page * PER_PAGE : (curr_page + 1) * PER_PAGE]
        answered = sum(1 for q in all_qs
                       if st.session_state.enneagram_answers.get(q["key"]) is not None)

        st.progress(answered / total_qs)
        st.caption(f"📖 Bölüm {curr_page + 1} / {total_pages}  •  "
                   f"✍️ {answered}/{total_qs} soru cevaplandı")
        st.divider()

        ennea_map = {
            1: "Kesinlikle Katılmıyorum",
            2: "Katılmıyorum",
            3: "Kararsızım",
            4: "Katılıyorum",
            5: "Kesinlikle Katılıyorum",
        }
        opts = [1, 2, 3, 4, 5]

        all_answered = True
        unanswered_nums = []
        for i, q in enumerate(page_qs):
            global_num = curr_page * PER_PAGE + i + 1
            is_missing = st.session_state.enneagram_answers.get(q["key"]) is None
            # Cevaplanmamış soruyu kırmızı çerçeveyle vurgula
            if is_missing and st.session_state.get("_ennea_show_missing", False):
                st.markdown(
                    f'<div style="border-left:4px solid #e74c3c; padding-left:10px;">'
                    f'<b style="color:#e74c3c;">❌ {global_num}. {q["text"]}</b></div>',
                    unsafe_allow_html=True,
                )
            else:
                st.write(f"**{global_num}. {q['text']}**")
            prev = st.session_state.enneagram_answers.get(q["key"])
            val  = st.radio(
                f"Soru {global_num}",
                opts,
                key=f"rad_{q['key']}",
                index=opts.index(prev) if prev is not None else None,
                horizontal=True,
                format_func=lambda x: ennea_map[x],
                label_visibility="collapsed",
            )
            if val is not None:
                st.session_state.enneagram_answers[q["key"]] = val
            else:
                all_answered = False
                unanswered_nums.append(global_num)
            st.divider()

        # Üstte de uyarı göster (scroll sorunu olmasın)
        if st.session_state.get("_ennea_show_missing", False) and unanswered_nums:
            nums_str = ", ".join(str(n) for n in unanswered_nums)
            st.error(f"⚠️ Cevaplanmamış sorular: **{nums_str}**  —  Lütfen yukarı kaydırarak eksikleri tamamla.")

        c1, c2 = st.columns(2)
        if curr_page > 0:
            if c1.button("⬅️ Önceki Bölüm"):
                st.session_state._ennea_show_missing = False
                st.session_state.enneagram_page -= 1
                st.session_state._scroll_top = True
                st.rerun()

        is_last = curr_page == total_pages - 1
        if not is_last:
            if c2.button("Sonraki Bölüm ➡️"):
                if not all_answered:
                    st.session_state._ennea_show_missing = True
                    nums_str = ", ".join(str(n) for n in unanswered_nums)
                    st.error(f"⚠️ Cevaplanmamış sorular: **{nums_str}**  —  Yukarı kaydırarak eksikleri tamamla.")
                    st.rerun()
                else:
                    st.session_state._ennea_show_missing = False
                    st.session_state.enneagram_page += 1
                    st.session_state._scroll_top = True
                    st.rerun()
        else:
            if c2.button("Bitir ve Gönder ✅", type="primary"):
                total_answered = sum(
                    1 for q in all_qs
                    if st.session_state.enneagram_answers.get(q["key"]) is not None
                )
                if total_answered < total_qs:
                    st.error(f"⚠️ Henüz {total_qs - total_answered} soru cevaplanmadı. "
                             "Önceki bölümlere dönerek eksikleri tamamla.")
                else:
                    with st.spinner("🧬 Kişilik haritan çıkarılıyor..."):
                        scores, rep = calculate_enneagram_report(
                            st.session_state.enneagram_answers
                        )
                        save_test_result_to_db(
                            st.session_state.student_id,
                            t_name,
                            st.session_state.enneagram_answers,
                            scores,
                            rep,
                        )
                        st.session_state.last_report = rep
                        st.session_state.page = "success_screen"
                        st.session_state._scroll_top = True
                        st.rerun()

    # ========================================
    # TİP: A/B SEÇİMLİ (Sağ-Sol Beyin)
    # ========================================
    elif q_type == "ab_choice":
        qs = data["questions"]
        PER_PAGE = 10
        tot_p = (len(qs) + PER_PAGE - 1) // PER_PAGE
        start = st.session_state.sayfa * PER_PAGE
        curr_qs = qs[start:start + PER_PAGE]

        st.progress((st.session_state.sayfa + 1) / tot_p)
        st.caption(f"📖 Sayfa {st.session_state.sayfa + 1} / {tot_p}")
        page_q_ids = []

        for q in curr_qs:
            qid = q["id"]
            page_q_ids.append(qid)
            st.write(f"**{qid}. {q['text']}**")
            prev = st.session_state.cevaplar.get(qid)
            options = [f"a) {q['a']}", f"b) {q['b']}"]
            idx = 0 if prev == "a" else (1 if prev == "b" else None)
            val = st.radio(f"Soru {qid}", options, key=f"q_{qid}", index=idx, horizontal=True, label_visibility="collapsed")
            if val:
                st.session_state.cevaplar[qid] = "a" if val.startswith("a)") else "b"
            st.divider()

        _navigate_pages(qs, page_q_ids, PER_PAGE, tot_p, t_name, q_type)

    # ========================================
    # TİP: DOĞRU/YANLIŞ (Çalışma Davranışı, Sınav Kaygısı)
    # ========================================
    elif q_type == "true_false":
        qs = data["questions"]
        PER_PAGE = 10
        tot_p = (len(qs) + PER_PAGE - 1) // PER_PAGE
        start = st.session_state.sayfa * PER_PAGE
        curr_qs = qs[start:start + PER_PAGE]

        st.progress((st.session_state.sayfa + 1) / tot_p)
        st.caption(f"📖 Sayfa {st.session_state.sayfa + 1} / {tot_p}")
        page_q_ids = []

        for q in curr_qs:
            qid = q["id"]
            page_q_ids.append(qid)
            st.write(f"**{qid}. {q['text']}**")
            prev = st.session_state.cevaplar.get(qid)
            options = ["Doğru", "Yanlış"]
            idx = 0 if prev == "D" else (1 if prev == "Y" else None)
            val = st.radio(f"Soru {qid}", options, key=f"q_{qid}", index=idx, horizontal=True, label_visibility="collapsed")
            if val:
                st.session_state.cevaplar[qid] = "D" if val == "Doğru" else "Y"
            st.divider()

        _navigate_pages(qs, page_q_ids, PER_PAGE, tot_p, t_name, q_type)

    # ========================================
    # TİP: ÇOKLU ZEKA LİSE (0-4 Likert)
    # ========================================
    elif q_type == "coklu_zeka_lise":
        qs = data["questions"]
        PER_PAGE = 10
        tot_p = (len(qs) + PER_PAGE - 1) // PER_PAGE
        start = st.session_state.sayfa * PER_PAGE
        curr_qs = qs[start:start + PER_PAGE]

        st.progress((st.session_state.sayfa + 1) / tot_p)
        st.caption(f"📖 Sayfa {st.session_state.sayfa + 1} / {tot_p}")
        page_q_ids = []

        likert_labels = {0: "0 - Asla", 1: "1 - Çok Az", 2: "2 - Bazen", 3: "3 - Çoğu Kez", 4: "4 - Daima"}
        likert_opts = [0, 1, 2, 3, 4]

        for q in curr_qs:
            qid = q["id"]
            page_q_ids.append(qid)
            st.write(f"**{qid}. {q['text']}**")
            prev = st.session_state.cevaplar.get(qid)
            idx = likert_opts.index(prev) if prev is not None else None
            val = st.radio(f"Soru {qid}", likert_opts, key=f"q_{qid}", index=idx, horizontal=True, format_func=lambda x: likert_labels[x], label_visibility="collapsed")
            if val is not None:
                st.session_state.cevaplar[qid] = val
            st.divider()

        _navigate_pages(qs, page_q_ids, PER_PAGE, tot_p, t_name, q_type)

    # ========================================
    # TİP: ÇOKLU ZEKA İLKÖĞRETİM (Evet/Hayır)
    # ========================================
    elif q_type == "coklu_zeka_ilk":
        qs = data["questions"]
        PER_PAGE = 10
        tot_p = (len(qs) + PER_PAGE - 1) // PER_PAGE
        start = st.session_state.sayfa * PER_PAGE
        curr_qs = qs[start:start + PER_PAGE]

        st.progress((st.session_state.sayfa + 1) / tot_p)
        st.caption(f"📖 Sayfa {st.session_state.sayfa + 1} / {tot_p}")
        page_q_ids = []

        for q in curr_qs:
            qid = q["id"]
            page_q_ids.append(qid)
            st.write(f"**{qid}. {q['text']}**")
            prev = st.session_state.cevaplar.get(qid)
            options = ["Evet", "Hayır"]
            idx = 0 if prev == "E" else (1 if prev == "H" else None)
            val = st.radio(f"Soru {qid}", options, key=f"q_{qid}", index=idx, horizontal=True, label_visibility="collapsed")
            if val:
                st.session_state.cevaplar[qid] = "E" if val == "Evet" else "H"
            st.divider()

        _navigate_pages(qs, page_q_ids, PER_PAGE, tot_p, t_name, q_type)

    # ========================================
    # TİP: VARK (Çoklu Seçim)
    # ========================================
    elif q_type == "vark_multi":
        qs = data["questions"]
        PER_PAGE = 8
        tot_p = (len(qs) + PER_PAGE - 1) // PER_PAGE
        start = st.session_state.sayfa * PER_PAGE
        curr_qs = qs[start:start + PER_PAGE]

        st.progress((st.session_state.sayfa + 1) / tot_p)
        st.caption(f"📖 Sayfa {st.session_state.sayfa + 1} / {tot_p}  •  💡 Her soruda birden fazla seçenek işaretleyebilirsin.")
        page_q_ids = []

        for q in curr_qs:
            qid = q["id"]
            page_q_ids.append(qid)
            st.write(f"**{qid}. {q['text']}**")
            prev = st.session_state.cevaplar.get(qid, [])
            selected = []
            for opt_key, opt_text in q["options"].items():
                checked = opt_key in prev
                if st.checkbox(f"{opt_key}) {opt_text}", value=checked, key=f"q_{qid}_{opt_key}"):
                    selected.append(opt_key)
            st.session_state.cevaplar[qid] = selected
            st.divider()

        _navigate_pages(qs, page_q_ids, PER_PAGE, tot_p, t_name, q_type)

    # ========================================
    # TİP: HOLLAND (5'li Likert)
    # ========================================
    elif q_type == "holland_5":
        qs = data["questions"]
        PER_PAGE = 10
        tot_p = (len(qs) + PER_PAGE - 1) // PER_PAGE
        start = st.session_state.sayfa * PER_PAGE
        curr_qs = qs[start:start + PER_PAGE]

        st.progress((st.session_state.sayfa + 1) / tot_p)
        st.caption(f"📖 Sayfa {st.session_state.sayfa + 1} / {tot_p}")
        page_q_ids = []

        holland_opts = [0, 1, 2, 3, 4]
        holland_labels = {
            0: "😣 Hiç Hoşlanmam",
            1: "😕 Hoşlanmam",
            2: "😐 Kararsızım",
            3: "😊 Hoşlanırım",
            4: "😍 Çok Hoşlanırım"
        }

        for q in curr_qs:
            qid = q["id"]
            page_q_ids.append(qid)
            st.write(f"**{qid}. {q['text']}**")
            prev = st.session_state.cevaplar.get(qid)
            idx = holland_opts.index(prev) if prev is not None else None
            val = st.radio(
                f"Soru {qid}", holland_opts, key=f"q_{qid}",
                index=idx, horizontal=True,
                format_func=lambda x: holland_labels[x],
                label_visibility="collapsed"
            )
            if val is not None:
                st.session_state.cevaplar[qid] = val
            st.divider()

        _navigate_pages(qs, page_q_ids, PER_PAGE, tot_p, t_name, q_type)

    # ========================================
    
    # ========================================
    # ========================================
    # TİP: P2 DİKKAT TESTİ
    # ========================================
    elif q_type == "p2_timed":
        current_row = st.session_state.p2_current_row
        time_per_row = st.session_state.get("p2_time_per_row", P2_CONFIG["time_per_row"])
        student_age = st.session_state.get("student_age", 15)

        # P2 CSS
        st.markdown(P2_CSS, unsafe_allow_html=True)

        # ---- ALIŞTIRMA SAYFASI ----
        if not st.session_state.p2_practice_done:
            practice = p2_generate_practice_row()

            # ADIM 2: Alıştırma sonuçları gösteriliyor
            if st.session_state.get("p2_practice_checked"):
                st.markdown("### ✅ Alıştırma Sonuçların")

                # Kayıtlı seçimleri al
                p_selected = st.session_state.get("p2_practice_selections", [])

                # İstatistikler
                total_targets = sum(1 for s in practice if s["is_target"])
                correct = 0
                missed = 0
                wrong = 0
                for i, sym in enumerate(practice):
                    sel = p_selected[i] if i < len(p_selected) else False
                    if sym["is_target"] and sel:
                        correct += 1
                    elif sym["is_target"] and not sel:
                        missed += 1
                    elif not sym["is_target"] and sel:
                        wrong += 1

                # Özet kutu
                if correct == total_targets and wrong == 0:
                    st.success(f"🎯 Mükemmel! Tüm hedefleri ({total_targets}/{total_targets}) doğru buldun, yanlış işaretleme yok.")
                else:
                    st.info(
                        f"🎯 **Doğru:** {correct}/{total_targets} hedef bulundu\n\n"
                        f"❌ **Kaçırılan:** {missed} hedef atlandı\n\n"
                        f"⚠️ **Yanlış:** {wrong} hedef olmayan işaretlendi"
                    )

                # Sembol bazlı sonuç gösterimi (renkli)
                result_parts = []
                for i, sym in enumerate(practice):
                    sel = p_selected[i] if i < len(p_selected) else False
                    is_missed = sym["is_target"] and not sel
                    is_wrong = not sym["is_target"] and sel
                    is_correct = sym["is_target"] and sel

                    if is_correct:
                        emoji = "✅"
                    elif is_missed:
                        emoji = "❌"
                    elif is_wrong:
                        emoji = "⚠️"
                    else:
                        emoji = "⬜"
                    above_str = "•" * sym["above"] if sym["above"] > 0 else " "
                    below_str = "•" * sym["below"] if sym["below"] > 0 else " "
                    result_parts.append(f"{emoji} {above_str} **{sym['letter']}** {below_str}")

                # 10'lu satırlar halinde göster
                P2_COLS = 10
                for sub_r in range((len(result_parts) + P2_COLS - 1) // P2_COLS):
                    cols = st.columns(P2_COLS)
                    for c in range(P2_COLS):
                        idx = sub_r * P2_COLS + c
                        if idx < len(result_parts):
                            with cols[c]:
                                st.markdown(result_parts[idx])

                st.markdown("---")
                st.markdown(
                    "**Renk Açıklaması:** ✅ Doğru seçim &nbsp;|&nbsp; "
                    "❌ Kaçırılan hedef &nbsp;|&nbsp; "
                    "⚠️ Yanlış işaretleme &nbsp;|&nbsp; "
                    "⬜ Doğru bırakılan"
                )
                st.markdown("---")

                if st.button("🚀 TESTE BAŞLA", type="primary", use_container_width=True):
                    st.session_state.p2_practice_done = True
                    st.session_state.p2_current_row = 0
                    st.session_state.p2_row_start = time.time()
                    st.session_state._scroll_top = True
                    st.rerun()

            # ADIM 1: Alıştırma formu
            else:
                st.markdown(
                    p2_render_practice_instructions_html(),
                    unsafe_allow_html=True,
                )

                with st.form("p2_practice"):
                    P2_COLS = 10
                    for sub_r in range((len(practice) + P2_COLS - 1) // P2_COLS):
                        cols = st.columns(P2_COLS)
                        for c in range(P2_COLS):
                            idx = sub_r * P2_COLS + c
                            if idx < len(practice):
                                with cols[c]:
                                    lbl = p2_render_symbol_label(practice[idx])
                                    st.checkbox(lbl, key=f"p2p_{idx}")

                    if st.form_submit_button("ALIŞTIRMAYI KONTROL ET", type="primary"):
                        # Seçimleri kaydet
                        selections = [
                            st.session_state.get(f"p2p_{i}", False)
                            for i in range(len(practice))
                        ]
                        st.session_state.p2_practice_selections = selections
                        st.session_state.p2_practice_checked = True
                        st.session_state._scroll_top = True
                        st.rerun()

        # ---- ANA TEST SATIRLARI ----
        elif 0 <= current_row < P2_CONFIG["rows"]:
            row_symbols = st.session_state.p2_rows[current_row]

            # Satır başlangıç zamanını kaydet (sadece ilk render'da)
            if st.session_state.p2_row_start is None:
                st.session_state.p2_row_start = time.time()

            # ── TEST EKRANI ──
            st.progress((current_row + 1) / P2_CONFIG["rows"])
            st.markdown(f"### Satır {current_row + 1} / {P2_CONFIG['rows']}")

            # ── JS GERI SAYIM — süre dolunca checkboxları kilitle ──
            components.html(f"""
            <!-- row:{current_row} ts:{int(time.time())} -->
            <div id="p2timer_{current_row}" style="text-align:center;font-size:2.2rem;font-weight:800;
                 color:#1B2A4A;padding:8px 0;font-family:monospace;">
              ⏱️ {time_per_row}
            </div>
            <script>
            (function(){{
              // Önceki satırdan kalan kilidi temizle
              try{{
                var doc = window.parent.document;
                var forms = doc.querySelectorAll('[data-testid="stForm"]');
                forms.forEach(function(f){{
                  f.style.opacity = '';
                  f.style.pointerEvents = '';
                }});
                var cbs = doc.querySelectorAll('[data-testid="stForm"] input[type="checkbox"]');
                cbs.forEach(function(cb){{
                  cb.disabled = false;
                  cb.style.pointerEvents = '';
                }});
              }}catch(e){{}}

              var left = {time_per_row};
              var el = document.getElementById('p2timer_{current_row}');
              if(!el) return;
              var iv = setInterval(function(){{
                left--;
                if(left <= 0){{
                  clearInterval(iv);
                  el.innerHTML = '⏰ Süre doldu! Otomatik gönderiliyor...';
                  el.style.color = '#E74C3C';
                  el.style.fontSize = '1.4rem';
                  try{{
                    var doc = window.parent.document;
                    var cbs = doc.querySelectorAll('[data-testid="stForm"] input[type="checkbox"]');
                    cbs.forEach(function(cb){{
                      cb.disabled = true;
                      cb.style.pointerEvents = 'none';
                    }});
                    var forms = doc.querySelectorAll('[data-testid="stForm"]');
                    forms.forEach(function(f){{
                      f.style.opacity = '0.5';
                      f.style.pointerEvents = 'none';
                    }});
                  }}catch(e){{}}
                  setTimeout(function(){{
                    try{{
                      var btns = window.parent.document.querySelectorAll(
                        '[data-testid="stFormSubmitButton"] button'
                      );
                      if(btns.length > 0) btns[btns.length-1].click();
                    }}catch(e){{}}
                  }}, 1000);
                }} else {{
                  el.innerHTML = '⏱️ ' + left;
                  if(left <= 3){{ el.style.color='#E74C3C'; el.style.fontSize='2.6rem'; }}
                  else if(left <= 7) el.style.color='#F39C12';
                }}
              }}, 1000);
            }})();
            </script>
            """, height=65)

            with st.form(f"p2_row_{current_row}"):
                P2_COLS = 10
                for sub_r in range(
                    (len(row_symbols) + P2_COLS - 1) // P2_COLS
                ):
                    cols = st.columns(P2_COLS)
                    for c in range(P2_COLS):
                        idx = sub_r * P2_COLS + c
                        if idx < len(row_symbols):
                            with cols[c]:
                                lbl = p2_render_symbol_label(row_symbols[idx])
                                st.checkbox(
                                    lbl,
                                    key=f"p2r{current_row}_s{idx}",
                                )

                submitted = st.form_submit_button(
                    "Satırı Gönder ➡️", type="primary"
                )

            if submitted:
                # Elapsed sadece KAYIT için — UI kontrolü yok
                elapsed_final = time.time() - (
                    st.session_state.p2_row_start or time.time()
                )
                selected = [
                    st.session_state.get(
                        f"p2r{current_row}_s{i}", False
                    )
                    for i in range(len(row_symbols))
                ]
                st.session_state.p2_row_results.append({
                    "symbols": row_symbols,
                    "selected": selected,
                    "elapsed_time": elapsed_final,
                })
                next_row = current_row + 1
                if next_row >= P2_CONFIG["rows"]:
                    _finish_p2_test(t_name)
                else:
                    st.session_state.p2_current_row = next_row
                    st.session_state.p2_row_start = time.time()
                    st.session_state._scroll_top = True
                    st.rerun()

    # ========================================
    # TİP: HIZLI OKUMA TESTİ (3 Fazlı)
    # ========================================
    elif q_type == "speed_reading":
        passage = st.session_state.sr_passage
        kademe = st.session_state.sr_kademe
        phase = st.session_state.sr_phase

        # ---- FAZ 1: OKUMA ----
        if phase == "reading":
            word_count = count_words(passage["text"])

            # Okuma başlatma anını kaydet
            if st.session_state.sr_start_time is None:
                st.session_state.sr_start_time = time.time()

            st.markdown(f"### 📖 {passage['title']}")
            st.markdown(f"<span style='color:#888; font-size:0.85rem;'>📝 {word_count} kelime</span>",
                        unsafe_allow_html=True)
            st.divider()

            # Zamanlayıcı göstergesi (canlı JS kronometre)
            elapsed = time.time() - st.session_state.sr_start_time
            start_secs = int(elapsed)

            components.html(f"""
            <div id="sr_timer" style="background: linear-gradient(135deg, #FFF3E0, #FFE0B2); border: 1px solid #FFB74D;
                        border-radius: 12px; padding: 12px 20px; margin: 0;
                        display: flex; align-items: center; gap: 12px;">
                <span style="font-size: 1.5rem;">⏱️</span>
                <div>
                    <div id="sr_clock" style="font-weight: 700; color: #E65100; font-size: 1.1rem; font-family: monospace;">
                        Okuma süresi: 00:00
                    </div>
                    <div style="font-size: 0.8rem; color: #888;">
                        Metni dikkatlice oku — bitirdiğinde aşağıdaki butona bas
                    </div>
                </div>
            </div>
            <script>
            (function(){{
                var elapsed = {start_secs};
                var el = document.getElementById('sr_clock');
                if(!el) return;
                function pad(n){{ return n < 10 ? '0'+n : ''+n; }}
                function update(){{
                    var m = Math.floor(elapsed / 60);
                    var s = elapsed % 60;
                    el.textContent = 'Okuma süresi: ' + pad(m) + ':' + pad(s);
                    if(elapsed >= 120){{ el.style.color = '#D32F2F'; }}
                    else if(elapsed >= 60){{ el.style.color = '#F57C00'; }}
                }}
                update();
                setInterval(function(){{ elapsed++; update(); }}, 1000);
            }})();
            </script>
            """, height=70)

            # Metin gösterimi
            paragraphs = passage["text"].split("\n\n")
            for para in paragraphs:
                if para.strip():
                    st.markdown(f"""
                        <div style="background: #ffffff; border: 1px solid #E8E8E8; border-radius: 10px;
                                    padding: 18px 22px; margin: 8px 0; font-size: 1.05rem;
                                    line-height: 1.8; color: #333; text-align: justify;">
                            {para.strip()}
                        </div>
                    """, unsafe_allow_html=True)

            st.markdown("")

            if st.button("✅ Okudum, Sorulara Geç", type="primary", use_container_width=True):
                reading_time = time.time() - st.session_state.sr_start_time
                st.session_state.sr_reading_time = reading_time
                st.session_state.sr_phase = "questions"
                st.session_state._scroll_top = True
                st.rerun()

            st.markdown("")
            st.info("💡 Metni hızlı ama dikkatli oku. Butona bastığında metin gizlenecek ve anlama soruları gelecek.")

        # ---- FAZ 2: ANLAMA SORULARI ----
        elif phase == "questions":
            questions = passage["questions"]
            reading_time = st.session_state.sr_reading_time
            mins = int(reading_time) // 60
            secs = int(reading_time) % 60

            st.markdown("### 🧠 Okuduğunu Anlama Soruları")

            st.markdown(f"""
                <div style="background: #E8F5E9; border: 1px solid #A5D6A7; border-radius: 12px;
                            padding: 12px 20px; margin: 10px 0;">
                    <span style="font-weight: 600; color: #2E7D32;">
                        ⏱️ Okuma süren: {mins} dk {secs} sn
                    </span>
                    <span style="color: #555; font-size: 0.85rem; margin-left: 10px;">
                        Şimdi metin hakkındaki soruları cevapla
                    </span>
                </div>
            """, unsafe_allow_html=True)

            st.warning("📌 Metin artık görünmüyor. Hatırladıklarına göre cevapla.")

            with st.form("sr_questions_form"):
                for i, q in enumerate(questions):
                    prev = st.session_state.sr_answers.get(q["id"])
                    keys = list(q["options"].keys())
                    idx_prev = keys.index(prev) if prev in keys else None
                    val = st.radio(
                        f"**{i + 1}. {q['text']}**",
                        keys,
                        index=idx_prev,
                        format_func=lambda k, o=q["options"]: f"{k}) {o[k]}",
                        key=f"sr_{q['id']}",
                    )
                    if val:
                        st.session_state.sr_answers[q["id"]] = val
                    st.divider()

                submitted = st.form_submit_button("Testi Bitir ✅", type="primary")

            if submitted:
                # Tüm sorular cevaplanmış mı kontrol et
                answered = sum(1 for q in questions if q["id"] in st.session_state.sr_answers)
                if answered < len(questions):
                    st.error(f"⚠️ {len(questions) - answered} soru boş kaldı. Lütfen tüm soruları cevapla.")
                else:
                    _finish_speed_reading_test(t_name)

    # ========================================
    # TİP: AKADEMİK ANALİZ (Bölümlü Performans)
    # ========================================
    elif q_type == "akademik_perf":
        akd_grade = st.session_state.get("akd_grade")
        akd_version = st.session_state.get("akd_version")
        sections = get_akademik_sections(grade=akd_grade, version=akd_version)
        sec_idx = st.session_state.akd_section_idx
        total_secs = len(sections)

        if sec_idx < total_secs:
            sec = sections[sec_idx]
            # Kademe etiketi
            KADEME_LABELS = {5: "5-6. Sınıf", 6: "5-6. Sınıf", 7: "7-8. Sınıf", 8: "7-8. Sınıf",
                             9: "9-10. Sınıf", 10: "9-10. Sınıf", 11: "11-12. Sınıf", 12: "11-12. Sınıf"}
            if akd_grade:
                ver_label = KADEME_LABELS.get(akd_grade, f"{akd_grade}. Sınıf")
            else:
                ver_label = "İlköğretim" if akd_version == "ilkogretim" else "Lise"

            st.markdown(
                f"### {sec['icon']} Bölüm {sec_idx + 1}/{total_secs}: "
                f"{sec['name']}"
            )
            st.progress((sec_idx + 1) / total_secs)
            st.caption(f"📎 Versiyon: {ver_label}")

            with st.form(f"akd_sec_{sec_idx}"):

                # ---- Okuma Anlama (metin + sorular) ----
                if sec["type"] == "passage_mc":
                    for p_idx, passage in enumerate(sec["data"]):
                        st.markdown(
                            f"<div style='background:#f8f9fa;border-left:4px solid "
                            f"#9B59B6;padding:15px;border-radius:8px;margin:10px 0;'>"
                            f"<b>📄 Metin {p_idx + 1}</b><br><br>"
                            f"{passage['passage']}</div>",
                            unsafe_allow_html=True,
                        )
                        for q in passage["questions"]:
                            prev = st.session_state.akd_answers.get(q["id"])
                            opts = list(q["options"].values())
                            keys = list(q["options"].keys())
                            idx_prev = (
                                keys.index(prev) if prev in keys else None
                            )
                            val = st.radio(
                                f"**{q['text']}**",
                                keys,
                                index=idx_prev,
                                format_func=lambda k, o=q["options"]: f"{k}) {o[k]}",
                                key=f"akd_{q['id']}",
                            )
                            if val:
                                st.session_state.akd_answers[q["id"]] = val
                            st.divider()

                # ---- Çoktan Seçmeli (matematik, mantık) ----
                elif sec["type"] == "mc":
                    for q in sec["data"]:
                        prev = st.session_state.akd_answers.get(q["id"])
                        keys = list(q["options"].keys())
                        idx_prev = (
                            keys.index(prev) if prev in keys else None
                        )
                        val = st.radio(
                            f"**{q['text']}**",
                            keys,
                            index=idx_prev,
                            format_func=lambda k, o=q["options"]: f"{k}) {o[k]}",
                            key=f"akd_{q['id']}",
                        )
                        if val:
                            st.session_state.akd_answers[q["id"]] = val
                        st.divider()

                # ---- Likert (öz-değerlendirme) ----
                elif sec["type"] == "likert":
                    likert_labels = {
                        1: "Hiç Katılmıyorum",
                        2: "Katılmıyorum",
                        3: "Kararsızım",
                        4: "Katılıyorum",
                        5: "Tamamen Katılıyorum",
                    }
                    for q in sec["data"]:
                        prev = st.session_state.akd_answers.get(q["id"])
                        idx_prev = (
                            prev - 1 if isinstance(prev, int) and 1 <= prev <= 5
                            else None
                        )
                        val = st.radio(
                            f"**{q['text']}**",
                            [1, 2, 3, 4, 5],
                            index=idx_prev,
                            format_func=lambda x: f"{x} — {likert_labels[x]}",
                            key=f"akd_{q['id']}",
                            horizontal=True,
                        )
                        if val:
                            st.session_state.akd_answers[q["id"]] = val
                        st.divider()

                # ---- Navigasyon butonları ----
                col_a, col_b = st.columns(2)
                with col_a:
                    if sec_idx > 0:
                        back = st.form_submit_button("⬅️ Önceki Bölüm")
                    else:
                        back = False
                with col_b:
                    if sec_idx < total_secs - 1:
                        nxt = st.form_submit_button(
                            "Sonraki Bölüm ➡️", type="primary"
                        )
                    else:
                        nxt = st.form_submit_button(
                            "Testi Bitir ✅", type="primary"
                        )

            if back:
                st.session_state.akd_section_idx = max(0, sec_idx - 1)
                st.session_state._scroll_top = True
                st.rerun()
            if nxt:
                if sec_idx < total_secs - 1:
                    st.session_state.akd_section_idx = sec_idx + 1
                    st.session_state._scroll_top = True
                    st.rerun()
                else:
                    _finish_akademik_test(t_name)


def app():
    # --- GENEL CSS ---
    st.markdown("""
    <style>
        /* ===== GLOBAL DARK MODE KORUMA (öğrenci sayfası) ===== */
        .stApp p, .stApp span, .stApp label,
        .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp li,
        .stApp [data-testid="stMarkdownContainer"] p,
        .stApp [data-testid="stWidgetLabel"] p {
            color: #0F172A !important;
        }
        [data-testid="stSidebar"] p, [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
            color: #FFFFFF !important;
        }
        .stApp button[kind="primary"] { color: white !important; }
        .stApp .stAlert p { color: inherit !important; }
        .motivation-box, .motivation-box h3, .motivation-box p { color: #FFFFFF !important; }
        .test-card-desc, .test-card-meta, .test-card-meta span, .stat-label, .sub-header { color: #555 !important; }
        .badge-done { color: #155724 !important; }
        .badge-ready { color: #0c5460 !important; }

        /* ===== ÖĞRENCİ GÖRÜNÜM CSS ===== */
        .main-header {
            text-align: center;
            font-weight: 900;
            font-size: 2.2rem;
            margin-bottom: 5px;
            color: #1B2A4A;
            letter-spacing: 1px;
        }
        .sub-header {
            text-align: center;
            margin-bottom: 25px;
            font-size: 1rem;
            color: #555;
        }
        
        /* ===== TEST KART TASARIMI ===== */
        .test-card {
            background: #ffffff;
            border: 1px solid #E0E4EA;
            border-radius: 16px;
            padding: 24px 20px;
            margin-bottom: 16px;
            text-align: center;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        .test-card::before {
            content: "";
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 4px;
            background: var(--card-color, #2E86C1);
        }
        .test-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
            border-color: var(--card-color, #2E86C1);
        }
        .test-card-icon {
            font-size: 2.5rem;
            margin-bottom: 8px;
        }
        .test-card-title {
            font-weight: 700;
            font-size: 1rem;
            color: #1B2A4A;
            margin-bottom: 6px;
        }
        .test-card-desc {
            font-size: 0.82rem;
            color: #777;
            margin-bottom: 10px;
            line-height: 1.4;
        }
        .test-card-meta {
            display: flex;
            justify-content: center;
            gap: 15px;
            font-size: 0.75rem;
            color: #999;
        }
        
        /* ===== DURUM BADGELERİ ===== */
        .badge-done {
            background: linear-gradient(135deg, #d4edda, #c3e6cb);
            color: #155724;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 700;
            display: inline-block;
            margin-top: 8px;
        }
        .badge-ready {
            background: linear-gradient(135deg, #d1ecf1, #bee5eb);
            color: #0c5460;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 700;
            display: inline-block;
            margin-top: 8px;
        }
        
        /* ===== İSTATİSTİK KUTUSU ===== */
        .stat-box {
            background: #ffffff;
            border: 1px solid #E0E4EA;
            border-radius: 14px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        }
        .stat-number {
            font-size: 2rem;
            font-weight: 800;
            color: #1B2A4A;
        }
        .stat-label {
            font-size: 0.8rem;
            color: #999;
            margin-top: 4px;
        }
        
        /* ===== İLERLEME ÇUBUĞU ===== */
        .progress-container {
            background: #E8EDF3;
            border-radius: 10px;
            height: 10px;
            overflow: hidden;
            margin: 10px 0;
        }
        .progress-bar {
            height: 100%;
            border-radius: 10px;
            background: linear-gradient(90deg, #1B2A4A, #2E86C1);
            transition: width 0.5s ease;
        }
        
        /* ===== MOTİVASYON MESAJLARI ===== */
        .motivation-box {
            background: linear-gradient(135deg, #1B2A4A 0%, #2C3E6B 100%);
            color: white;
            border-radius: 16px;
            padding: 25px;
            text-align: center;
            margin: 20px 0;
        }
        .motivation-box h3 {
            color: #FFFFFF;
            margin-bottom: 8px;
        }
    </style>
    """, unsafe_allow_html=True)

    # --- BAŞLIK ---

    st.markdown("<h1 class='main-header'>🎓 EĞİTİM CHECK UP</h1>", unsafe_allow_html=True)
    st.markdown(f"<div class='sub-header'>Hoşgeldin <b>{st.session_state.student_name}</b> — Kendini keşfetmeye hazır mısın?</div>", unsafe_allow_html=True)

    if "page" not in st.session_state:
        st.session_state.page = "home"

    ALL_TESTS = [
        "Enneagram Kişilik Testi",
        "Çalışma Davranışı Ölçeği",
        "Sağ-Sol Beyin Dominansı Testi",
        "Sınav Kaygısı Ölçeği",
        "VARK Öğrenme Stilleri Testi",
        "Çoklu Zeka Testi",
        "Holland Mesleki İlgi Envanteri",
        "P2 Dikkat Testi",
        "Akademik Analiz Testi",
        "Hızlı Okuma Testi",
    ]

    # ============================================================
    # SAYFA 1: ANA MENÜ (HOME)
    # ============================================================
    if st.session_state.page == "home":
        
        # --- İSTATİSTİK KUTUSU ---
        # PERFORMANS: Tek sorgu ile tüm test durumlarını al (9 ayrı DB bağlantısı yerine 1)
        completed_tests = get_completed_tests(st.session_state.student_id)
        completed_count = sum(1 for t in ALL_TESTS if t in completed_tests)
        total_count = len(ALL_TESTS)
        pct = round(completed_count / total_count * 100)
        
        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            st.markdown(f"""
                <div class="stat-box">
                    <div class="stat-number">{completed_count}/{total_count}</div>
                    <div class="stat-label">Tamamlanan Test</div>
                </div>
            """, unsafe_allow_html=True)
        with sc2:
            st.markdown(f"""
                <div class="stat-box">
                    <div class="stat-number">%{pct}</div>
                    <div class="stat-label">İlerleme Oranı</div>
                </div>
            """, unsafe_allow_html=True)
        with sc3:
            remaining = total_count - completed_count
            st.markdown(f"""
                <div class="stat-box">
                    <div class="stat-number">{remaining}</div>
                    <div class="stat-label">Kalan Test</div>
                </div>
            """, unsafe_allow_html=True)
        
        # İlerleme Çubuğu
        st.markdown(f"""
            <div class="progress-container">
                <div class="progress-bar" style="width: {pct}%;"></div>
            </div>
        """, unsafe_allow_html=True)
        
        # Tüm testler tamamlandıysa kutlama mesajı
        if completed_count == total_count:
            st.markdown("""
                <div class="motivation-box">
                    <h3>🎉 Tebrikler! Tüm Testleri Tamamladın!</h3>
                    <p>Harika bir iş çıkardın. Öğretmenin artık sana özel bir analiz raporu hazırlayabilir.</p>
                </div>
            """, unsafe_allow_html=True)
        else:
            # Motivasyon mesajları
            motivations = [
                "Her test, kendini daha iyi tanımana bir adım daha yaklaştırıyor. 🌟",
                "Doğru veya yanlış cevap yok — sadece SEN varsın! 💪",
                "Kendini keşfetmek, geleceğine yatırım yapmaktır. 🚀",
                "Her cevabın, sana özel bir yol haritası çiziyor. 🗺️",
            ]
            st.info(f"💡 {random.choice(motivations)}")
        
        st.markdown("---")
        
        # --- TEST KARTLARI ---
        col1, col2 = st.columns(2)
        
        for idx, test in enumerate(ALL_TESTS):
            is_done = test in completed_tests
            target_col = col1 if idx % 2 == 0 else col2
            meta = TEST_META.get(test, {})
            
            with target_col:
                if is_done:
                    st.markdown(f"""
                        <div class="test-card" style="--card-color: #27AE60; opacity: 0.85;">
                            <div class="test-card-icon">{meta.get('icon', '📝')}</div>
                            <div class="test-card-title">{test}</div>
                            <div class="test-card-desc">{meta.get('desc', '')}</div>
                            <span class="badge-done">✅ Tamamlandı</span>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                        <div class="test-card" style="--card-color: {meta.get('color', '#2E86C1')};">
                            <div class="test-card-icon">{meta.get('icon', '📝')}</div>
                            <div class="test-card-title">{test}</div>
                            <div class="test-card-desc">{meta.get('desc', '')}</div>
                            <div class="test-card-meta">
                                <span>⏱️ {meta.get('duration', '~10 dk')}</span>
                                <span>📝 {meta.get('questions', '?')} soru</span>
                            </div>
                            <span class="badge-ready">🎯 Hazır</span>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"▶️ {test} Başla", key=test, type="primary"):
                        st.session_state.selected_test = test
                        st.session_state.intro_passed = False

                        if "Enneagram" in test:
                            flat = []
                            for tip_no, qs in ENNEAGRAM_QUESTIONS.items():
                                for i, text in enumerate(qs):
                                    flat.append({"type": tip_no, "idx": i, "text": text,
                                                 "key": f"{tip_no}_{i}"})
                            random.shuffle(flat)
                            st.session_state.enneagram_shuffled  = flat
                            st.session_state.enneagram_page      = 0
                            st.session_state.enneagram_answers   = {}
                            st.session_state.current_test_data   = {"type": "enneagram_fixed"}

                        elif "Sağ-Sol Beyin" in test:
                            st.session_state.current_test_data = {"type": "ab_choice", "questions": SAG_SOL_BEYIN_QUESTIONS}
                            st.session_state.cevaplar = {}
                            st.session_state.sayfa = 0

                        elif "Çalışma Davranışı" in test:
                            st.session_state.current_test_data = {"type": "true_false", "questions": CALISMA_DAVRANISI_QUESTIONS}
                            st.session_state.cevaplar = {}
                            st.session_state.sayfa = 0

                        elif "Sınav Kaygısı" in test:
                            st.session_state.current_test_data = {"type": "true_false", "questions": SINAV_KAYGISI_QUESTIONS}
                            st.session_state.cevaplar = {}
                            st.session_state.sayfa = 0

                        elif "Çoklu Zeka" in test:
                            student_grade = st.session_state.get('student_grade')
                            student_age = st.session_state.get('student_age', 15)
                            is_ilkogretim = (student_grade and student_grade <= 8) or (not student_grade and student_age and student_age <= 13)
                            if is_ilkogretim:
                                qs = []
                                for zk in ZEKA_SIRA:
                                    qs.extend(COKLU_ZEKA_QUESTIONS_ILKOGRETIM[zk])
                                st.session_state.current_test_data = {"type": "coklu_zeka_ilk", "questions": qs}
                            else:
                                qs = []
                                for zk in ZEKA_SIRA:
                                    qs.extend(COKLU_ZEKA_QUESTIONS_LISE[zk])
                                st.session_state.current_test_data = {"type": "coklu_zeka_lise", "questions": qs}
                            st.session_state.cevaplar = {}
                            st.session_state.sayfa = 0

                        elif "VARK" in test:
                            st.session_state.current_test_data = {"type": "vark_multi", "questions": VARK_QUESTIONS}
                            st.session_state.cevaplar = {}
                            st.session_state.sayfa = 0

                        elif "Holland" in test:
                            st.session_state.current_test_data = {"type": "holland_5", "questions": HOLLAND_QUESTIONS}
                            st.session_state.cevaplar = {}
                            st.session_state.sayfa = 0

                        elif "P2 Dikkat" in test:
                            seed = hash(str(st.session_state.student_id) + str(time.time()))
                            student_age = st.session_state.get("student_age", 15)
                            st.session_state.current_test_data = {"type": "p2_timed"}
                            st.session_state.p2_rows = generate_p2_test(seed=seed)
                            st.session_state.p2_current_row = -1   # -1 = yönerge, -2 = alıştırma
                            st.session_state.p2_row_results = []
                            st.session_state.p2_practice_done = False
                            st.session_state.p2_practice_checked = False
                            st.session_state.p2_instructions_done = False
                            st.session_state.p2_row_start = None
                            st.session_state.p2_time_per_row = p2_get_time_per_row(student_age)

                        elif "Akademik Analiz" in test:
                            student_grade = st.session_state.get("student_grade")
                            if student_grade:
                                # Grade bilgisi var — doğrudan 4 kademe sistemi
                                st.session_state.current_test_data = {
                                    "type": "akademik_perf",
                                    "grade": student_grade,
                                }
                                st.session_state.akd_version = None
                                st.session_state.akd_grade = student_grade
                            else:
                                # Grade bilgisi yok (eski kayıt) — yaşa göre fallback
                                student_age = st.session_state.get("student_age", 15)
                                version = "ilkogretim" if student_age and student_age <= 13 else "lise"
                                st.session_state.current_test_data = {
                                    "type": "akademik_perf",
                                    "version": version,
                                }
                                st.session_state.akd_version = version
                                st.session_state.akd_grade = None
                            st.session_state.akd_section_idx = 0
                            st.session_state.akd_answers = {}

                        elif "Hızlı Okuma" in test:
                            student_grade = st.session_state.get("student_grade")
                            if not student_grade:
                                student_age = st.session_state.get("student_age", 15)
                                if student_age <= 11:
                                    student_grade = 5
                                elif student_age <= 13:
                                    student_grade = 7
                                elif student_age <= 15:
                                    student_grade = 9
                                else:
                                    student_grade = 11
                            passage_data, kademe = get_passage_for_grade(student_grade)
                            st.session_state.current_test_data = {"type": "speed_reading"}
                            st.session_state.sr_passage = passage_data
                            st.session_state.sr_kademe = kademe
                            st.session_state.sr_phase = "reading"  # reading → questions → done
                            st.session_state.sr_start_time = None  # okuma başladığında set edilecek
                            st.session_state.sr_reading_time = None
                            st.session_state.sr_answers = {}

                        st.session_state.page = "test"
                        st.session_state._scroll_top = True
                        st.rerun()

    # ============================================================
    # SAYFA 2: BAŞARI EKRANI
    # ============================================================
    elif st.session_state.page == "success_screen":
        st.markdown("""
            <div class="motivation-box">
                <h3>🎉 Harika İş Çıkardın!</h3>
                <p>Testi başarıyla tamamladın. Sonuçların öğretmenine iletildi.</p>
            </div>
        """, unsafe_allow_html=True)

        if "last_report" in st.session_state and st.session_state.last_report:
            with st.expander("📋 Raporunu Görüntüle", expanded=True):
                st.markdown(st.session_state.last_report)

        # P2 Dikkat Testi — Satır Bazlı Hata Analizi
        if st.session_state.get("p2_analysis_html"):
            with st.expander("🔍 Satır Bazlı Hata Analizi", expanded=True):
                st.markdown(st.session_state.p2_analysis_html)

        st.markdown("---")
        c1, c2 = st.columns(2)
        if c1.button("🏠 Diğer Teste Geç", type="primary"):
            st.session_state.page = "home"
            st.session_state._scroll_top = True
            st.rerun()
        if c2.button("🚪 Çıkış Yap"):
            st.session_state.clear()
            st.session_state._scroll_top = True
            st.rerun()

    # ============================================================
    # SAYFA 3: TEST ÇÖZME EKRANI
    # ============================================================
    elif st.session_state.page == "test":
        t_name = st.session_state.selected_test
        meta = TEST_META.get(t_name, {})

        # --- GİRİŞ EKRANI ---
        if not st.session_state.intro_passed:
            st.markdown(f"### {meta.get('icon', '📝')} {t_name}")
            
            # Test bilgi kartı
            st.markdown(f"""
                <div style="background: #ffffff; border: 1px solid #E0E4EA; border-radius: 16px; padding: 25px; margin: 15px 0;
                            border-top: 4px solid {meta.get('color', '#2E86C1')};">
                    <p style="color: #555; font-size: 1rem; margin-bottom: 15px;">{meta.get('desc', '')}</p>
                    <div style="display: flex; gap: 20px; color: #777; font-size: 0.9rem;">
                        <span>⏱️ Tahmini süre: <b>{meta.get('duration', '~10 dk')}</b></span>
                        <span>📝 <b>{meta.get('questions', '?')}</b> soru</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            st.info("💡 Doğru veya yanlış cevap yoktur. İçinden geldiği gibi, samimiyetle cevapla.")
            
            # --- HIZLI OKUMA TESTİ İÇİN ÖZEL BİLGİ ---
            if "Hızlı Okuma" in t_name:
                from hizli_okuma_engine import KADEME_LABELS as HO_KADEME_LABELS, WPM_NORMS
                kademe = st.session_state.get("sr_kademe", "kademe_2")
                norms = WPM_NORMS.get(kademe, WPM_NORMS["kademe_2"])
                kademe_label = HO_KADEME_LABELS.get(kademe, "")
                passage = st.session_state.get("sr_passage", {})
                word_count = count_words(passage.get("text", "")) if passage else 0

                st.markdown(f"""
                <div style="background: #FFF3E0; border: 1px solid #FFB74D; border-radius: 12px;
                            padding: 20px; margin: 10px 0;">
                    <div style="font-weight: 700; color: #E65100; font-size: 1.05rem; margin-bottom: 12px;">
                        📖 Test Nasıl İşler?
                    </div>
                    <div style="font-size: 0.92rem; color: #444; line-height: 1.7;">
                        <b>1.</b> Sana yaş grubuna uygun bir metin gösterilecek ({word_count} kelime)<br>
                        <b>2.</b> Zamanlayıcı otomatik başlayacak — metni dikkatlice oku<br>
                        <b>3.</b> "Okudum" butonuna bastığında metin gizlenecek<br>
                        <b>4.</b> 10 anlama sorusu gelecek — hafızana güven!<br>
                        <b>5.</b> Hem okuma hızın hem de anlama oranın raporlanacak
                    </div>
                    <div style="margin-top: 15px; padding-top: 12px; border-top: 1px dashed #FFB74D;">
                        <div style="font-weight: 600; color: #E65100; margin-bottom: 8px;">
                            📊 Yaş Grubu Normların ({kademe_label}):
                        </div>
                        <table style="width: 100%; border-collapse: collapse; font-size: 0.88rem;">
                            <tr style="background: #FFF8E1;">
                                <th style="padding: 6px 10px; text-align: left; color: #E65100;">Seviye</th>
                                <th style="padding: 6px 10px; text-align: center; color: #E65100;">Kelime/Dk</th>
                            </tr>
                            <tr><td style="padding: 5px 10px;">🔴 Çok Yavaş</td><td style="text-align:center;">&lt; {norms['cok_yavas']}</td></tr>
                            <tr style="background:#fafafa;"><td style="padding: 5px 10px;">🟠 Yavaş</td><td style="text-align:center;">{norms['cok_yavas']} – {norms['yavas']}</td></tr>
                            <tr><td style="padding: 5px 10px;">🟡 Ortalama</td><td style="text-align:center;">{norms['yavas']} – {norms['hizli']}</td></tr>
                            <tr style="background:#fafafa;"><td style="padding: 5px 10px;">🔵 Hızlı</td><td style="text-align:center;">{norms['hizli']} – {norms['cok_hizli']}</td></tr>
                            <tr><td style="padding: 5px 10px;">🟢 Çok Hızlı</td><td style="text-align:center;">&gt; {norms['cok_hizli']}</td></tr>
                        </table>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            
            # --- P2 DİKKAT TESTİ İÇİN YAŞA GÖRE SÜRE BİLGİSİ ---
            if "P2 Dikkat" in t_name:
                student_age = st.session_state.get("student_age", 15)
                my_time = p2_get_time_per_row(student_age)

                # Süre bilgi kartı
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #EBF5FB 0%, #D6EAF8 100%);
                            border: 1px solid #AED6F1; border-radius: 14px;
                            padding: 22px 24px; margin: 14px 0;">
                    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 16px;">
                        <div style="background: #2563EB; color: white; width: 42px; height: 42px;
                                    border-radius: 12px; display: flex; align-items: center;
                                    justify-content: center; font-size: 1.3rem; flex-shrink: 0;">⏱️</div>
                        <div>
                            <div style="font-weight: 700; color: #1B2A4A; font-size: 1.05rem;">
                                Senin Süren: <span style="color: #2563EB; font-size: 1.25rem;">{my_time} saniye</span>
                                <span style="color: #888; font-size: 0.85rem; font-weight: 400;"> / satır</span>
                            </div>
                            <div style="font-size: 0.82rem; color: #666; margin-top: 2px;">
                                Yaşın: {student_age} — süre otomatik belirlendi
                            </div>
                        </div>
                    </div>
                    <table style="width: 100%; border-collapse: separate; border-spacing: 0;
                                  font-size: 0.88rem; border-radius: 10px; overflow: hidden;
                                  border: 1px solid #D4E6F1;">
                        <tr style="background: #2563EB; color: white;">
                            <th style="padding: 10px 14px; text-align: left; font-weight: 600;">Yaş Grubu</th>
                            <th style="padding: 10px 14px; text-align: center; font-weight: 600;">Satır Süresi</th>
                        </tr>
                        <tr style="background: {'#D5F5E3' if student_age <= 9 else '#fff'};">
                            <td style="padding: 9px 14px; border-bottom: 1px solid #EAF2F8;">
                                {'<b>➤ ' if student_age <= 9 else ''}7 – 9 yaş{'</b>' if student_age <= 9 else ''}</td>
                            <td style="padding: 9px 14px; text-align: center; border-bottom: 1px solid #EAF2F8;">
                                {'<b>' if student_age <= 9 else ''}25 saniye{'</b>' if student_age <= 9 else ''}</td>
                        </tr>
                        <tr style="background: {'#D5F5E3' if 10 <= student_age <= 12 else '#F8FBFF'};">
                            <td style="padding: 9px 14px; border-bottom: 1px solid #EAF2F8;">
                                {'<b>➤ ' if 10 <= student_age <= 12 else ''}10 – 12 yaş{'</b>' if 10 <= student_age <= 12 else ''}</td>
                            <td style="padding: 9px 14px; text-align: center; border-bottom: 1px solid #EAF2F8;">
                                {'<b>' if 10 <= student_age <= 12 else ''}20 saniye{'</b>' if 10 <= student_age <= 12 else ''}</td>
                        </tr>
                        <tr style="background: {'#D5F5E3' if 13 <= student_age <= 15 else '#fff'};">
                            <td style="padding: 9px 14px; border-bottom: 1px solid #EAF2F8;">
                                {'<b>➤ ' if 13 <= student_age <= 15 else ''}13 – 15 yaş{'</b>' if 13 <= student_age <= 15 else ''}</td>
                            <td style="padding: 9px 14px; text-align: center; border-bottom: 1px solid #EAF2F8;">
                                {'<b>' if 13 <= student_age <= 15 else ''}15 saniye{'</b>' if 13 <= student_age <= 15 else ''}</td>
                        </tr>
                        <tr style="background: {'#D5F5E3' if student_age >= 16 else '#F8FBFF'};">
                            <td style="padding: 9px 14px;">
                                {'<b>➤ ' if student_age >= 16 else ''}16+ yaş{'</b>' if student_age >= 16 else ''}</td>
                            <td style="padding: 9px 14px; text-align: center;">
                                {'<b>' if student_age >= 16 else ''}12 saniye{'</b>' if student_age >= 16 else ''}</td>
                        </tr>
                    </table>
                </div>
                """, unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            
            if c1.button("⬅️ Vazgeç / Ana Menü"):
                st.session_state.page = "home"
                st.session_state._scroll_top = True
                st.rerun()
                
            if c2.button("HAZIRIM, BAŞLA! 🚀", type="primary"):
                st.session_state.intro_passed = True
                st.session_state._scroll_top = True
                st.rerun()

        # --- SORULAR ---
        else:
            # --- ÜST BAR: Test adı + Ana Menüye Dön butonu ---
            bar_col1, bar_col2 = st.columns([3, 1])
            with bar_col1:
                st.markdown(f"#### {meta.get('icon', '📝')} {t_name}")
            with bar_col2:
                if st.button("🏠 Testlere Dön", key="btn_back_to_home"):
                    st.session_state.show_exit_confirm = True

            # Onay diyaloğu
            if st.session_state.get("show_exit_confirm", False):
                st.warning("⚠️ Testten çıkmak istediğine emin misin? Cevapların **kaydedilmeyecek**.")
                conf_c1, conf_c2 = st.columns(2)
                with conf_c1:
                    if st.button("✅ Evet, çıkmak istiyorum", key="confirm_exit_yes"):
                        st.session_state.show_exit_confirm = False
                        st.session_state.page = "home"
                        st.session_state._scroll_top = True
                        st.rerun()
                with conf_c2:
                    if st.button("❌ Hayır, teste devam et", key="confirm_exit_no", type="primary"):
                        st.session_state.show_exit_confirm = False
                        st.rerun()

            st.markdown("---")
            _render_test_questions()

    # ============================================================
    # 📌 SCROLL TO TOP — TÜM İÇERİK RENDER EDİLDİKTEN SONRA
    # ============================================================
    if st.session_state.get("_scroll_top"):
        st.session_state._scroll_top = False
        components.html(
            """<script>
            (function(){
                function doScroll(){
                    try{
                        var m = window.parent.document.querySelector('section.main');
                        if(m) m.scrollTo({top:0, behavior:'instant'});
                        var c = window.parent.document.querySelector('[data-testid="stAppViewContainer"]');
                        if(c) c.scrollTo({top:0, behavior:'instant'});
                        var s = window.parent.document.querySelector('[data-testid="stMain"]');
                        if(s) s.scrollTo({top:0, behavior:'instant'});
                        window.parent.scrollTo(0,0);
                    }catch(e){}
                }
                doScroll();
                setTimeout(doScroll, 100);
                setTimeout(doScroll, 300);
                setTimeout(doScroll, 600);
                setTimeout(doScroll, 1200);
            })();
            </script>""", height=0,
        )


# ============================================================

# P2 TEST BİTİRME FONKSİYONU
# ============================================================
def _finish_p2_test(t_name):
    """P2 testini puanla, rapor üret, hata analizi ekle ve veritabanına kaydet."""
    row_results = st.session_state.p2_row_results

    with st.spinner("📊 P2 sonuçların hesaplanıyor..."):
        scores = calculate_p2(row_results, time_per_row=st.session_state.get("p2_time_per_row"))
        report = generate_p2_report(scores)

        # Hata analizi HTML'ini rapora ekle
        analysis_html = p2_render_full_analysis_html(scores)

        scores_for_db = {
            "TN": scores["TN"], "E1": scores["E1"],
            "E2": scores["E2"], "E": scores["E"],
            "TN_E": scores["TN_E"], "CP": scores["CP"],
            "FR": scores["FR"],
            "hit_rate": scores["hit_rate"],
            "error_pct": scores["error_pct"],
            "cp_pct": scores["cp_pct"],
            "level": scores["level"],
            "balance": scores["balance"],
            "consistency": scores["consistency"],
            "row_performances": scores["row_performances"],
            "row_details_summary": [
                {
                    "row_num": d["row_num"],
                    "correct": d["correct"],
                    "missed": d["missed"],
                    "wrong": d["wrong"],
                    "blank": d["blank"],
                    "cp": d["cp"],
                }
                for d in scores["row_details"]
            ],
            "student_age": st.session_state.get("student_age"),
            "time_per_row": st.session_state.get("p2_time_per_row", P2_CONFIG["time_per_row"]),
        }

        raw_answers = {
            f"row_{i}": {
                "selected": r["selected"],
                "elapsed_time": round(r["elapsed_time"], 2),
            }
            for i, r in enumerate(row_results)
        }

        save_test_result_to_db(
            st.session_state.student_id, t_name,
            raw_answers, scores_for_db, report,
        )

        # Hata analizi HTML'ini session'a kaydet (success ekranında göstermek için)
        st.session_state.p2_analysis_html = analysis_html
        st.session_state.last_report = report
        st.session_state.page = "success_screen"
        st.session_state._scroll_top = True
        st.rerun(scope="app")


# ============================================================
# AKADEMİK ANALİZ TEST BİTİRME FONKSİYONU
# ============================================================
def _finish_speed_reading_test(t_name):
    """Hızlı okuma testini puanla, rapor üret ve veritabanına kaydet."""
    answers = st.session_state.sr_answers
    passage = st.session_state.sr_passage
    kademe = st.session_state.sr_kademe
    reading_time = st.session_state.sr_reading_time

    with st.spinner("📊 Hızlı okuma sonuçların hesaplanıyor..."):
        scores = calculate_speed_reading(answers, passage, reading_time, kademe)
        report = generate_speed_reading_report(scores)

        scores_for_db = {
            "wpm": scores["wpm"],
            "speed_label": scores["speed_label"],
            "comprehension_pct": scores["comprehension_pct"],
            "comp_level": scores["comp_level"],
            "effective_score": scores["effective_score"],
            "eff_level": scores["eff_level"],
            "profile": scores["profile"],
            "reading_time_seconds": scores["reading_time_seconds"],
            "word_count": scores["word_count"],
            "correct": scores["correct"],
            "total": scores["total"],
            "kademe": kademe,
        }

        save_test_result_to_db(
            st.session_state.student_id, t_name,
            answers, scores_for_db, report,
        )

        st.session_state.last_report = report
        st.session_state.page = "success_screen"
        st.session_state._scroll_top = True
        st.rerun(scope="app")


def _finish_akademik_test(t_name):
    """Akademik analiz testini puanla, rapor üret ve veritabanına kaydet."""
    answers = st.session_state.akd_answers
    akd_grade = st.session_state.get("akd_grade")
    akd_version = st.session_state.get("akd_version")

    with st.spinner("📊 Akademik analiz sonuçların hesaplanıyor..."):
        scores = calculate_akademik(answers, grade=akd_grade, version=akd_version)
        report = generate_akademik_report(scores)

        scores_for_db = {
            "version": akd_version,
            "grade": akd_grade,
            "overall": scores["overall"],
            "level": scores["level"],
            "performance_avg": scores["performance_avg"],
            "self_assessment": scores["self_assessment"],
            "strongest": scores["strongest"]["name"],
            "weakest": scores["weakest"]["name"],
        }
        for sec_name, sec_data in scores["sections"].items():
            key = sec_name.split(" ")[-1] if " " in sec_name else sec_name
            scores_for_db[key] = sec_data["pct"]

        save_test_result_to_db(
            st.session_state.student_id, t_name,
            answers, scores_for_db, report,
        )

        st.session_state.last_report = report
        st.session_state.page = "success_screen"
        st.session_state._scroll_top = True
        st.rerun(scope="app")  # Fragment'tan çık, tam sayfa geçişi


# ============================================================
# SAYFA NAVİGASYONU + TEST BİTİRME (ORTAK FONKSİYON)
# ============================================================
def _navigate_pages(qs, page_q_ids, PER_PAGE, tot_p, t_name, q_type):
    """İleri/Geri navigasyon ve test bitirme mantığı."""
    c1, c2 = st.columns(2)

    if st.session_state.sayfa > 0:
        if c1.button("⬅️ Geri"):
            st.session_state.sayfa -= 1
            st.session_state._scroll_top = True
            st.rerun()

    if st.session_state.sayfa < tot_p - 1:
        if c2.button("İleri ➡️"):
            missing = _check_missing(page_q_ids, q_type)
            if missing:
                st.error("⚠️ Bu sayfada boş bıraktığın sorular var. Onları doldurmadan geçemezsin.")
            else:
                st.session_state.sayfa += 1
                st.session_state._scroll_top = True
                st.rerun()
    else:
        if c2.button("Testi Bitir ✅", type="primary"):
            all_ids = [q["id"] for q in qs]
            missing = _check_missing(all_ids, q_type)
            if missing:
                st.error(f"⚠️ Eksik sorular var ({len(missing)} adet)! Lütfen kontrol et.")
            else:
                _finish_and_save(t_name, q_type)


def _check_missing(q_ids, q_type):
    """Cevaplanmamış soruları döndürür."""
    missing = []
    for qid in q_ids:
        ans = st.session_state.cevaplar.get(qid)
        if q_type == "vark_multi":
            if not ans:
                missing.append(qid)
        else:
            if ans is None:
                missing.append(qid)
    return missing


def _finish_and_save(t_name, q_type):
    """Testi puanla, raporu üret ve veritabanına kaydet."""
    answers = st.session_state.cevaplar
    scores = None
    report = ""

    with st.spinner("📊 Sonuçların hesaplanıyor..."):

        if q_type == "ab_choice":
            result, report = calculate_sag_sol_beyin(answers)
            scores = {
                "sag_beyin": result["sag_beyin"], "sol_beyin": result["sol_beyin"],
                "sag_yuzde": result["sag_yuzde"], "sol_yuzde": result["sol_yuzde"],
                "dominant": result["dominant"], "level": result["level"],
            }

        elif q_type == "true_false":
            if "Çalışma Davranışı" in t_name:
                result, report = calculate_calisma_davranisi(answers)
                scores = {"total": result["total"], "max_total": result["max_total"], "categories": result["categories"]}
            elif "Sınav Kaygısı" in t_name:
                result, report = calculate_sinav_kaygisi(answers)
                scores = {"total": result["total"], "total_pct": result["total_pct"], "level": result["overall_level"], "categories": result["categories"]}

        elif q_type == "coklu_zeka_lise":
            result, report = calculate_coklu_zeka_lise(answers)
            scores = {zk: result["scores"][zk]["pct"] for zk in result["scores"]}

        elif q_type == "coklu_zeka_ilk":
            result, report = calculate_coklu_zeka_ilkogretim(answers)
            scores = {zk: result["scores"][zk]["pct"] for zk in result["scores"]}

        elif q_type == "vark_multi":
            result, report = calculate_vark(answers)
            scores = {
                "V": result["counts"]["V"], "A": result["counts"]["A"],
                "R": result["counts"]["R"], "K": result["counts"]["K"],
                "dominant": result["dominant"][0]
            }

        elif q_type == "holland_5":
            result, report = calculate_holland(answers)
            scores = {
                "R": result["R"], "I": result["I"], "A": result["A"],
                "S": result["S"], "E": result["E"], "C": result["C"],
                "holland_code": result["holland_code"],
            }

        save_test_result_to_db(st.session_state.student_id, t_name, answers, scores, report)

        st.session_state.last_report = report
        st.session_state.page = "success_screen"
        st.session_state._scroll_top = True
        st.rerun(scope="app")  # Fragment'tan çık, tam sayfa geçişi
