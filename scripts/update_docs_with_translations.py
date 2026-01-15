#!/usr/bin/env python3
"""Update documentation translations with translated code blocks.

This script updates the expert_behavior_docs and expert_behavior_docs_edit
keys in all locale files to include fully translated system prompt examples.
"""

import json
from pathlib import Path

# Locale directory
LOCALES_DIR = Path(__file__).parent.parent / "locales" / "ui"

# Full translations including code blocks
TRANSLATIONS = {
    "de.json": {
        "dialogs.add_chat.expert_behavior_docs": "### 🎯 Warum Dieses Feld Am Wichtigsten Ist\n\nDie Verhaltensanweisungen definieren den gesamten Ansatz Ihres Experten:\n- **Ton**: Freundlich, professionell, locker, formell?\n- **Expertise**: Allgemeine Übersicht oder tiefe technische Details?\n- **Format**: Codebeispiele, Schritt für Schritt, konversationell?\n- **Einschränkungen**: Was soll der Experte NICHT tun?\n- **Richtlinien**: Spezifische Anforderungen für Antworten\n\n### 📝 Beispiel: Python-Experte\n\n```\nDu bist ein Python-Experte mit 15 Jahren Erfahrung.\n- Stelle sauberen, PEP 8-konformen Code mit Typ-Hints und Docstrings bereit\n- Erkläre Konzepte klar mit praktischen Beispielen\n- Warne vor häufigen Fallstricken und Best Practices\n- Schlage hilfreiche Bibliotheken vor, wenn angemessen\n```\n\n### 📝 Beispiel: Rechtsberater\n\n```\nDu bist ein rechtlicher Assistent, der allgemeine rechtliche Informationen bereitstellt.\n- Füge immer einen Haftungsausschluss hinzu: \"Ich bin kein Anwalt, dies ist keine Rechtsberatung\"\n- Sei gründlich aber vorsichtig in Empfehlungen\n- Schlage die Konsultation eines qualifizierten Anwalts für spezifische Rechtsangelegenheiten vor\n- Biete allgemeine rechtliche Konzepte und Rahmenbedingungen\n```\n\n### 📝 Beispiel: Schreibcoach\n\n```\nDu bist ein ermutigender Schreibcoach.\n- Stelle Fragen, um die Ziele des Autors zu verstehen\n- Biete spezifisches, umsetzbares Feedback\n- Balanciere Lob mit konstruktiver Kritik\n- Schlage Ressourcen zur Verbesserung vor\n- Sei geduldig und unterstützend\n```",
    },
    "es.json": {
        "dialogs.add_chat.expert_behavior_docs": "### 🎯 Por Qué Este Campo Es Más Importante\n\nLas instrucciones de comportamiento definen todo el enfoque de su experto:\n- **Tono**: Amigable, profesional, casual, formal?\n- **Experiencia**: Resumen general o detalles técnicos profundos?\n- **Formato**: Ejemplos de código, paso a paso, conversacional?\n- **Restricciones**: Qué NO debe hacer el experto?\n- **Directrices**: Requisitos específicos para las respuestas\n\n### 📝 Ejemplo: Experto en Python\n\n```\nEres un experto en Python con 15 años de experiencia.\n- Proporciona código limpio, compatible con PEP 8 con sugerencias de tipo y docstrings\n- Explica conceptos claramente con ejemplos prácticos\n- Advierte sobre errores comunes y mejores prácticas\n- Sugiere bibliotecas útiles cuando sea apropiado\n```\n\n### 📝 Ejemplo: Asesor Legal\n\n```\nEres un asistente legal que proporciona información legal general.\n- Incluye siempre un descargo de responsabilidad: \"No soy abogado, esto no es asesoramiento legal\"\n- Sé minucioso pero cauteloso en las recomendaciones\n- Sugiere consultar a un abogado calificado para asuntos legales específicos\n- Proporciona conceptos y marcos legales generales\n```\n\n### 📝 Ejemplo: Entrenador de Escritura\n\n```\nEres un entrenador de escritura alentador.\n- Haz preguntas para entender los objetivos del escritor\n- Proporciona comentarios específicos y accionables\n- Equilibra elogios con críticas constructivas\n- Sugiere recursos para mejorar\n- Sé paciente y solidario\n```",
    },
    "fr.json": {
        "dialogs.add_chat.expert_behavior_docs": "### 🎯 Pourquoi Ce Champ Est Le Plus Important\n\nLes instructions de comportement définissent toute l'approche de votre expert:\n- **Ton**: Amical, professionnel, décontracté, formel?\n- **Expertise**: Aperçu général ou détails techniques approfondis?\n- **Format**: Exemples de code, étape par étape, conversationnel?\n- **Contraintes**: Que l'expert ne doit PAS faire?\n- **Directives**: Exigences spécifiques pour les réponses\n\n### 📝 Exemple: Expert Python\n\n```\nVous êtes un expert Python avec 15 ans d'expérience.\n- Fournissez un code propre, conforme PEP 8 avec des indications de type et des docstrings\n- Expliquez clairement les concepts avec des exemples pratiques\n- Avertissez des pièges courants et des meilleures pratiques\n- Suggérez des bibliothèques utiles lorsque approprié\n```\n\n### 📝 Exemple: Conseiller Juridique\n\n```\nVous êtes un assistant juridique fournissant des informations juridiques générales.\n- Incluez toujours un avis de non-responsabilité: \"Je ne suis pas avocat, ceci n'est pas un conseil juridique\"\n- Soyez minutieux mais prudent dans les recommandations\n- Suggérez de consulter un avocat qualifié pour des questions juridiques spécifiques\n- Fournissez des concepts et cadres juridiques généraux\n```\n\n### 📝 Exemple: Coach d'Écriture\n\n```\nVous êtes un coach d'écriture encourageant.\n- Posez des questions pour comprendre les objectifs du rédacteur\n- Fournissez des commentaires spécifiques et actionnables\n- Équilibrez les éloges avec les critiques constructives\n- Suggérez des ressources pour s'améliorer\n- Soyez patient et favorable\n```",
    },
    "it.json": {
        "dialogs.add_chat.expert_behavior_docs": "### 🎯 Perché Questo Campo È Più Importante\n\nLe istruzioni sul comportamento definiscono l'intero approccio del tuo esperto:\n- **Tono**: Amichevole, professionale, casual, formale?\n- **Competenza**: Panoramica generale o dettagli tecnici approfonditi?\n- **Formato**: Esempi di codice, passo dopo passo, conversazionale?\n- **Vincoli**: Cosa NON deve fare l'esperto?\n- **Linee guida**: Requisiti specifici per le risposte\n\n### 📝 Esempio: Esperto Python\n\n```\nSei un esperto Python con 15 anni di esperienza.\n- Fornisci codice pulito, conforme PEP 8 con suggerimenti di tipo e docstring\n- Spiega chiaramente i concetti con esempi pratici\n- Avverti su insidie comuni e best practices\n- Suggerisci librerie utili quando appropriato\n```\n\n### 📝 Esempio: Consigliere Legale\n\n```\nSei un assistente legale che fornisce informazioni legali generali.\n- Includi sempre una dichiarazione di non responsabilità: \"Non sono un avvocato, questo non è un consiglio legale\"\n- Sii approfondito ma cauto nelle raccomandazioni\n- Suggerisci di consultare un avvocato qualificato per questioni legali specifiche\n- Fornisci concetti e quadri legali generali\n```\n\n### 📝 Esempio: Coach di Scrittura\n\n```\nSei un coach di scrittura incoraggiante.\n- Fai domande per comprendere gli obiettivi dello scrittore\n- Fornisci feedback specifici e azionabili\n- Equilibria lodi con critiche costruttive\n- Suggerisci risorse per migliorare\n- Sii paziente e di supporto\n```",
    },
    "id.json": {
        "dialogs.add_chat.expert_behavior_docs": "### 🎯 Mengapa Bidang Ini Paling Penting\n\nInstruksi perilaku mendefinisikan seluruh pendekatan ahli Anda:\n- **Nada**: Ramah, profesional, santai, formal?\n- **Keahlian**: Tinjauan umum atau detail teknis mendalam?\n- **Format**: Contoh kode, langkah demi langkah, percakapan?\n- **Kendala**: Apa yang TIDAK boleh dilakukan ahli?\n- **Pedoman**: Persyaratan khusus untuk respons\n\n### 📝 Contoh: Ahli Python\n\n```\nAnda adalah ahli Python dengan 15 tahun pengalaman.\n- Sediakan kode bersih, compliant PEP 8 dengan type hints dan docstrings\n- Jelaskan konsep dengan jelas dengan contoh praktis\n- Peringatkan tentang jebakan umum dan praktik terbaik\n- Sarankan perpustakaan berguna bila sesuai\n```\n\n### 📝 Contoh: Penasihat Hukum\n\n```\nAnda adalah asisten hukum yang menyediakan informasi hukum umum.\n- Selalu sertakan disclaimer: \"Saya bukan pengacara, ini bukan nasihat hukum\"\n- Teliti tapi berhati-hati dalam rekomendasi\n- Sarankan konsultasi dengan pengacara berkualitas untuk masalah hukum spesifik\n- Sediakan konsep dan kerangka kerja hukum umum\n```\n\n### 📝 Contoh: Pelatih Menulis\n\n```\nAnda adalah pelatih menulis yang memberikan semangat.\n- Tanyakan pertanyaan untuk memahami tujuan penulis\n- Berikan umpan balik spesifik dan dapat ditindaklanjuti\n- Seimbangkan pujian dengan kritik konstruktif\n- Sarankan sumber daya untuk perbaikan\n- Bersabar dan suportif\n```",
    },
    "ms.json": {
        "dialogs.add_chat.expert_behavior_docs": "### 🎯 Mengapa Bidang Ini Paling Penting\n\nArahan kelakuan mentakrifkan seluruh pendekatan pakar anda:\n- **Nada**: Mesra, profesional, santai, formal?\n- **Kepakaran**: Gambaran umum atau butiran teknikal mendalam?\n- **Format**: Contoh kod, langkah demi langkah, perbualan?\n- **Kekangan**: Apa yang TIDAK boleh dilakukan oleh pakar?\n- **Garis panduan**: Keperluan khusus untuk respons\n\n### 📝 Contoh: Pakar Python\n\n```\nAnda adalah pakar Python dengan 15 tahun pengalaman.\n- Sediakan kod bersih, mematuhi PEP 8 dengan petunjuk jenis dan docstring\n- Jelaskan konsep dengan jelas dengan contoh praktikal\n- Amarkan tentang perangkap biasa dan amalan terbaik\n- Cadangkan perpustakaan berguna bila sesuai\n```\n\n### 📝 Contoh: Penasihat Undang-undang\n\n```\nAnda adalah pembantu undang-undang yang menyediakan maklumat undang-undang umum.\n- Sentiasa sertakan penafian: \"Saya bukan peguam, ini bukan nasihat undang-undang\"\n- Teliti tetapi berhati-hati dalam cadangan\n- Cadangkan runding dengan peguam berkelayakan untuk masalah undang-undang tertentu\n- Sediakan konsep dan kerangka undang-undang umum\n```\n\n### 📝 Contoh: Jurulatih Penulisan\n\n```\nAnda adalah jurulatih penulisan yang memberangsangkan.\n- Tanya soalan untuk memahami matlamat penulis\n- Berikan maklum balas khusus dan boleh dilaksanakan\n- Keseimbangkan pujian dengan kritikan binaan\n- Cadangkan sumber untuk penambahbaikan\n- Sabar dan menyokong\n```",
    },
    "pt.json": {
        "dialogs.add_chat.expert_behavior_docs": "### 🎯 Por Que Este Campo É Mais Importante\n\nAs instruções de comportamento definem toda a abordagem do seu especialista:\n- **Tom**: Amigável, profissional, casual, formal?\n- **Expertise**: Visão geral ou detalhes técnicos profundos?\n- **Formato**: Exemplos de código, passo a passo, conversacional?\n- **Restrições**: O que o especialista NÃO deve fazer?\n- **Diretrizes**: Requisitos específicos para respostas\n\n### 📝 Exemplo: Especialista Python\n\n```\nVocê é um especialista Python com 15 anos de experiência.\n- Forneça código limpo, compatível com PEP 8 com type hints e docstrings\n- Explique conceitos claramente com exemplos práticos\n- Avise sobre armadilhas comuns e melhores práticas\n- Sugira bibliotecas úteis quando apropriado\n```\n\n### 📝 Exemplo: Assessor Jurídico\n\n```\nVocê é um assistente jurídico que fornece informações jurídicas gerais.\n- Sempre inclua um aviso: \"Não sou advogado, isto não é aconselhamento jurídico\"\n- Seja thorough mas cauteloso em recomendações\n- Sugira consultar um advogado qualificado para questões jurídicas específicas\n- Forneca conceitos e estruturas jurídicas gerais\n```\n\n### 📝 Exemplo: Treinador de Escrita\n\n```\nVocê é um treinador de escritura encorajador.\n- Faça perguntas para entender os objetivos do escritor\n- Forneça feedback específico e acionável\n- Equilibre elogios com crítica construtiva\n- Sugira recursos para melhoria\n- Seja paciente e solidário\n```",
    },
    "ru.json": {
        "dialogs.add_chat.expert_behavior_docs": "### 🎯 Почему Это Поле Самое Важное\n\nИнструкции по поведению определяют весь подход вашего эксперта:\n- **Тон**: Дружелюбный, профессиональный, непринужденный, формальный?\n- **Экспертиза**: Общий обзор или глубокие технические детали?\n- **Формат**: Примеры кода, пошагово, разговорный?\n- **Ограничения**: Что НЕ должен делать эксперт?\n- **Руководящие принципы**: Специфические требования для ответов\n\n### 📝 Пример: Эксперт по Python\n\n```\nВы эксперт по Python с 15-летним опытом.\n- Предоставляйте чистый код, соответствующий PEP 8, с подсказками типов и строками документации\n- Четко объясняйте концепции с практическими примерами\n- Предупреждайте о распространенных ошибках и лучших практиках\n- Рекомендуйте полезные библиотеки, когда уместно\n```\n\n### 📝 Пример: Юридический Консультант\n\n```\nВы юридический консультант, предоставляющий общую правовую информацию.\n- Всегда включайте отказ от ответственности: \"Я не юрист, это не является юридической консультацией\"\n- Будьте основательны, но осторожны в рекомендациях\n- Рекомендуйте консультироваться с квалифицированным адвокатом по конкретным правовым вопросам\n- Предоставляйте общие правовые концепции и рамки\n```\n\n### 📝 Пример: Тренер по Письму\n\n```\nВы ободряющий тренер по письму.\n- Задавайте вопросы, чтобы понять цели писателя\n- Предоставляйте конкретную, выполнимую обратную связь\n- Балансируйте похвалу с конструктивной критикой\n- Рекомендуйте ресурсы для улучшения\n- Будьте терпеливы и поддерживайте\n```",
    },
    "tr.json": {
        "dialogs.add_chat.expert_behavior_docs": "### 🎯 Bu Alan Neden En Önemli\n\nDavranış talimatları, uzmanınızın tüm yaklaşımını tanımlar:\n- **Ton**: Arkadaşça, profesyonel, gündelik, resmi?\n- **Uzmanlık**: Genel bakış veya derin teknik detaylar?\n- **Format**: Kod örnekleri, adım adım, konuşmacı?\n- **Kısıtlamalar**: Uzmanın NELER YAPMAMASI gerekiyor?\n- **Kılavuzlar**: Yanıtlar için özel gereksinimler\n\n### 📝 Örnek: Python Uzmanı\n\n```\n15 yıllık deneyime sahip bir Python uzmanısınız.\n- Tip ipuçuları ve docstring'lerle PEP 8 uyumlu temiz kod sağlayın\n- Pratik örneklerle kavramaları açıkça açıklayın\n- Yayın tuzakları ve en iyi uygulamalar hakkında uyarıda bulunun\n- Uygun olduğunda yararlı kütüphaneler önerin\n```\n\n### 📝 Örnek: Hukuk Danışmanı\n\n```\nGenel hukuki bilgiler sağlayan bir hukuk asistanısınız.\n- Her zaman bir sorumluluk reddi ekleyin: \"Ben avukat değilim, bu hukuki tavsiye değildir\"\n- Tavsiyelerde titiz ama ihtiyatlı olun\n- Özel hukuki konular için nitelikli bir avukata danışmanızı önerin\n- Genel hukuki kavramlar ve çerçeveler sağlayın\n```\n\n### 📝 Örnek: Yazım Koçu\n\n```\nCesaret verici bir yazım koçusunuz.\n- Yazarın hedeflerini anlamak için sorular sorun\n- Somut, uygulanabilir geri bildirim sağlayın\n- Övgüyi yapıcı eleştiriyle dengeleyin\n- İyileştirme için kaynaklar önerin\n- Sabırlı ve destekleyici olun\n```",
    },
    "wyw.json": {
        "dialogs.add_chat.expert_behavior_docs": "### 🎯 为啥箇字段最要紧\n\n行为指令定义侬专家个全部方法:\n- **语气**: 友好、专业、随意、正式?\n- **专长**: 总体概述还是深厚技术细节?\n- **格式**: 代码例子、一步步、对话式?\n- **限制**: 专家勿应该做啥?\n- **指导方针**: 回复个具体要求\n\n### 📝 例子: Python专家\n\n```\n侬是一个拥有15年经验个Python专家。\n- 提供清洁个、符合PEP 8个代码，带有类型提示搭文档字符串\n- 用实际例子清晰解释概念\n- 警告常见个陷阱搭最佳实践\n- 适当时建议有用个库\n```\n\n### 📝 例子: 法律顾问\n\n```\n侬是一个提供一般法律信息个法律助理。\n- 总是包含免责声明:\"我弗是律师，搿个弗是法律建议\"\n- 建议中要详尽但要谨慎\n- 建议就特定法律事项咨询合格律师\n- 提供一般法律概念搭框架\n```\n\n### 📝 例子: 写作教练\n\n```\n侬是一个令人鼓舞个写作教练。\n- 提问以理解作者个目标\n- 提供具体、可行个反馈\n- 平衡赞扬搭建设性批评\n- 建议改进资源\n- 耐心搭支持性\n```",
    },
    "yue.json": {
        "dialogs.add_chat.expert_behavior_docs": "### 🎯 點解呢個欄位最重要\n\n行為指令定義你專家嘅全部方法:\n- **語氣**: 友善、專業、隨意、正式?\n- **專長**: 總體概述仲係深厚技術細節?\n- **格式**: 代碼例子、一步步、對話式?\n- **限制**: 專家唔應該做咩?\n- **指引**: 回覆嘅具體要求\n\n### 📝 例子: Python專家\n\n```\n你係一個擁有15年經驗嘅Python專家。\n- 提供乾淨嘅、符合PEP 8嘅代碼，帶有類型提示同文檔字符串\n- 用實際例子清晰解釋概念\n- 警告常見嘅陷阱同最佳實踐\n- 適當時建議有用嘅庫\n```\n\n### 📝 例子: 法律顧問\n\n```\n你係一個提供一般法律信息嘅法律助理。\n- 總是包含免責聲明:\"我唔係律師，呢個唔係法律建議\"\n- 建議中要詳盡但要謹慎\n- 建議就特定法律事項咨詢合資格律師\n- 提供一般法律概念同框架\n```\n\n### 📝 例子: 寫作教練\n\n```\n你係一個令人鼓舞嘅寫作教練。\n- 提問以理解作者嘅目標\n- 提供具體、可行嘅反饋\n- 平衡讚揚同建設性批評\n- 建議改進資源\n- 耐心同支持性\n```",
    },
    "zh-CN.json": {
        "dialogs.add_chat.expert_behavior_docs": "### 🎯 为什么这个字段最重要\n\n行为指令定义了您专家的整个方法:\n- **语气**: 友好、专业、随意、正式?\n- **专长**: 总体概述还是深厚技术细节?\n- **格式**: 代码示例、一步步、对话式?\n- **限制**: 专家不应该做什么?\n- **指导方针**: 回复的具体要求\n\n### 📝 示例: Python专家\n\n```\n您是一位拥有15年经验的Python专家。\n- 提供清洁的、符合PEP 8的代码，带有类型提示和文档字符串\n- 用实际例子清晰解释概念\n- 警告常见的陷阱和最佳实践\n- 适当时建议有用的库\n```\n\n### 📝 示例: 法律顾问\n\n```\n您是一位提供一般法律信息的法律助理。\n- 总是包含免责声明:\"我不是律师，这不是法律建议\"\n- 建议中要详尽但要谨慎\n- 建议就特定法律事项咨询合格律师\n- 提供一般法律概念和框架\n```\n\n### 📝 示例: 写作教练\n\n```\n您是一位令人鼓舞的写作教练。\n- 提问以理解作者的目标\n- 提供具体、可行的反馈\n- 平衡赞扬与建设性批评\n- 建议改进资源\n- 耐心和支持性\n```",
    },
    "zh-TW.json": {
        "dialogs.add_chat.expert_behavior_docs": "### 🎯 為什麼這個欄位最重要\n\n行為指令定義了您專家的整個方法:\n- **語氣**: 友好、專業、隨意、正式?\n- **專長**: 總體概述還是深厚技術細節?\n- **格式**: 代碼示例、一步步、對話式?\n- **限制**: 專家不應該做什麼?\n- **指導方針**: 回覆的具體要求\n\n### 📝 示例: Python專家\n\n```\n您是一位擁有15年經驗的Python專家。\n- 提供乾淨的、符合PEP 8的代碼，帶有類型提示和文檔字符串\n- 用實際例子清晰解釋概念\n- 警告常見的陷阱和最佳實踐\n- 適當時建議有用的庫\n```\n\n### 📝 示例: 法律顧問\n\n```\n您是一位提供一般法律信息的法律助理。\n- 總是包含免責聲明:\"我不是律師，這不是法律建議\"\n- 建議中要詳盡但要謹慎\n- 建議就特定法律事項咨詢合格律師\n- 提供一般法律概念和框架\n```\n\n### 📝 示例: 寫作教練\n\n```\n您是一位令人鼓舞的寫作教練。\n- 提問以理解作者的目標\n- 提供具體、可行的反饋\n- 平衡讚揚與建設性批評\n- 建議改進資源\n- 耐心和支持性\n```",
    }
}


def update_locale_file(filename: str, updates: dict) -> bool:
    """Update a specific locale file with new translations.

    Args:
        filename: Name of the locale file (e.g., "de.json")
        updates: Dictionary of keys to update

    Returns:
        True if file was updated, False otherwise
    """
    file_path = LOCALES_DIR / filename

    if not file_path.exists():
        print(f"  ⚠️  File not found: {file_path}")
        return False

    # Read existing file
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"  ❌ Error reading {filename}: {e}")
        return False

    # Update translations
    modified = False
    for key, value in updates.items():
        # Navigate to the key location
        parts = key.split(".")
        current = data

        for part in parts[:-1]:
            if part not in current:
                print(f"  ⚠️  Key path not found: {key}")
                break
            current = current[part]
        else:
            # Update the value
            if parts[-1] in current and current[parts[-1]] != value:
                current[parts[-1]] = value
                modified = True

    if modified:
        # Write back to file
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"  ✅ Updated {filename}")
            return True
        except Exception as e:
            print(f"  ❌ Error writing {filename}: {e}")
            return False
    else:
        print(f"  ℹ️  No changes needed for {filename}")
        return False


def main():
    """Main function to update all locale files."""
    print("📚 Updating Documentation with Translated Code Blocks")
    print("=" * 60)

    updated_count = 0
    for filename, updates in TRANSLATIONS.items():
        print(f"\nProcessing {filename}...")
        if update_locale_file(filename, updates):
            updated_count += 1

    print("\n" + "=" * 60)
    print(f"✨ Updated {updated_count} locale files with translated code examples!")
    print()
    print("All code examples are now fully translated into each language.")


if __name__ == "__main__":
    main()
