# Widgets
This package contains Qt widgets implemented to match the style and behavior of the native Houdini widgets with additional facilities.

#### InputField (QLineEdit)
- `Esc` to clear field
- `Ctrl+MMB` to reset to the default value

#### FilterField (InputField)
- Corresponding text placeholder
- `accepted` signal emitted on `Enter`

#### Slider (QSlider)
- Direct jump to click position
- Access to Houdini's _Value ladder_ with `MMB`
- **Todo**: `Ctrl+MMB` to reset to the default value
