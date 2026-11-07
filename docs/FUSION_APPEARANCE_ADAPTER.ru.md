# Адаптер Fusion Appearance — пропускание и мутность

[English](FUSION_APPEARANCE_ADAPTER.md)

Статус: экспериментальный адаптер SDK, проверенный только автономными тестами с имитациями. Пакет НЕ содержит полноценную палитру или интерфейс установки. Рендеринг, сохранение и повторное открытие в Fusion не проверялись.

## Сопоставление с Filamentra v1

Данные наследуются так же, как в исходном каталоге: пресет → линейка → цвет.

| Поле | Сопоставление Autodesk Fusion | Точность |
| --- | --- | --- |
| HEX/непрозрачная alpha | `Appearance.color = Color.create(...)` | Прямое |
| `surface_type` | `AppearanceSurfaceTypes.*` и `Appearances.add` | Прямое |
| `roughness` | `Appearance.roughness` | Прямое при `haze = 0` |
| `normal_gl` | `Appearance.normalTexture` | Прямое при наличии локального ресурса |
| `textures.roughness` | `Appearance.roughnessTexture` | Прямое при `haze = 0` |
| `ior` | `appearanceProperties.itemById('transparent_ior').value` | Прямое при проверке во время выполнения |
| `attenuation_distance_mm` | `itemById('transparent_distance').value` | Прямое только при известных единицах и обратном чтении |
| `transmission` | `TransparentAppearanceSurface` вместо числового значения | Приблизительное; числовая интенсивность не применяется |
| `haze` | Более высокая шероховатость поверхности | Приблизительное; меняет отражения и не является объёмным рассеянием |

Документированного независимого свойства Fusion API для мутности или точной числовой доли пропускания света НЕТ. Адаптер НЕ преобразует ни одно из них в alpha. Неподдерживаемые сопоставления, отсутствующие PBR-ресурсы, свойства только для чтения, нераспознанные единицы и снижение точности описываются в возвращаемом `FusionAppearanceReport` (`exact`, `approximate`, `unavailable`).

Для мутных материалов безопаснее пропустить исходную карту шероховатости, чем позволить ей незаметно отменить числовую шероховатость, добавленную для имитации мутности.

Адаптер преобразует расстояние затухания с помощью единиц, возвращаемых `FloatProperty.units`; если единицы установить не удалось, свойство отмечается как недоступное без предположений. Нейтральный цвет предпросмотра Clear — условность рендерера, а НЕ утверждение об измеренном HEX производителя.

## Пример внутри Autodesk Fusion (июль 2026 и новее)

    from filamentra.fusion_appearance import install_catalog_color

    report = install_catalog_color(
        design, line, color, presets_by_id,
        texture_root="/path/to/local/extracted/catalog",
    )
    print(report.exact)
    print(report.approximate)
    print(report.unavailable)

Этот код устанавливает Appearance в Design. Он не применяет внешний вид к геометрии и не изменяет выбранные тела.

Официальные источники:
https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/core_Appearance.htm
https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/core_AppearanceSurfaceTypes.htm
https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/core_FloatProperty_units.htm

## Приёмка в реальном Fusion не завершена

Запустите тест на поддерживаемой сборке Fusion в macOS и Windows. Создайте PLA Translucent, PETG Translucent и PETG Clear в одном Design. Проверьте IOR, единицы затухания и шероховатость. Выполните рендер образцов с толщиной стенки 0,8, 2 и 10 мм с фиксированным логотипом 4FusionLab позади них. Проверьте сохранение и повторное открытие и опишите различия между окном Design и рабочей средой Render. Без этой проверки не заявляйте полную оптическую эквивалентность Filamentra Pages.
