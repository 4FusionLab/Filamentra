# Разработка Filamentra

Filamentra — планируемый Fusion add-in для поиска филаментов и установки визуальных Appearances. Рабочие Python-модули существуют, но полного установочного аддона пока нет.

## Общие правила 4FusionLab

- Общие стандарты: https://github.com/4FusionLab/.github/blob/main/AGENTS.md; модель общего CI: https://github.com/4FusionLab/.github/blob/main/RELEASE_PLATFORM.md.
- Общайся и составляй планы на русском, код и UI Fusion — на английском. Сохраняй независимые README.md и README.ru.md.
- Перед изменениями изучай текущие файлы и Git-статус. Conventional Commits; предпочтительно PR с успешными проверками, прямой push в main допускается.
- Не меняй UUID Fusion manifest, IDs команд, поддержку ОС и формат пакета без миграционного плана. Не коммить секреты, токены или личные CAD-файлы.
- Где есть runtime, релиз создаёт push или merge в main только для файлов из .github/release-paths.txt после успешного CI. GitVersion.Tool 6.8.2, неизменяемый автоматический тег и GitHub Release; теги вручную не создавай.
- Изменение docs, README, тестов, AGENTS.md или CI само по себе не должно выпускать релиз. Общие Actions подключай только по конкретному commit SHA.
- Unit-тесты и ZIP не заменяют нативную проверку Autodesk Fusion. Сохраняй существующие ограничения и доказательства совместимости.

## Правила реализации

- Сверяй реализованные возможности с README.md, README.ru.md и docs/ROADMAP.md. Не представляй задуманные UI, скачивание каталога или установку в Fusion как готовые функции.
- Основные модули: filamentra/appearance_mapping.py, filamentra/fusion_appearance.py и filamentra/texture_generator.py. Сохраняй детерминизм, provenance и границы реального Fusion API.
- Данные Filamentra-DataSource — визуальные приближения, а не сертифицированные механические или оптические параметры. Не изобретай производителей, SKU и оттенки.
- Сейчас релиз распространяет исходный ZIP Python-модулей и SHA-256, а не готовый Fusion installer. Изменение формата пакета требует отдельной проверки.
- Выполняй `python -m unittest discover -s tests -v`, `python scripts/build_release.py --version X.Y.Z` и проверку checksum. Нативную работу в Fusion утверждай только после отдельного CAD-теста.
