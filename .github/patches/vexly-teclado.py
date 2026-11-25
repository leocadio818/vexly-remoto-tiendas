# Vexly: cambia la barra de teclas especiales del iPhone por el panel en cuadricula.
# Se aplica al compilar (tiendas-ios.yml); no se guarda en el codigo de Canela.
p = "flutter/lib/mobile/pages/remote_page.dart"
s = open(p, encoding="utf-8").read()
ini = s.index("class KeyHelpTools extends StatefulWidget {")
fin = s.index("class ImagePaint extends StatelessWidget {")
viejo = """            KeyHelpTools(
                keyboardIsVisible: keyboardIsVisible,
                showGestureHelp: _showGestureHelp),"""
assert s.count(viejo) == 1, "no encontre la llamada a KeyHelpTools"
s = s[:ini] + r"""class KeyHelpTools extends StatefulWidget {
  final bool keyboardIsVisible;
  final bool showGestureHelp;
  final VoidCallback openKeyboard;

  /// need to show by external request, etc [keyboardIsVisible] or [changeTouchMode]
  bool get requestShow => keyboardIsVisible || showGestureHelp;

  KeyHelpTools(
      {required this.keyboardIsVisible,
      required this.showGestureHelp,
      required this.openKeyboard});

  @override
  State<KeyHelpTools> createState() => _KeyHelpToolsState();
}

// Vexly: panel de teclas especiales en cuadricula, con colores por grupo.
class _KeyHelpToolsState extends State<KeyHelpTools> {
  var _panel = false;
  double? _lastH;
  final _key = GlobalKey();

  static const _gris = [Color(0xFF2A2E37), Color(0xFF3A3F4B), Color(0xFFE8EAF0)];
  static const _fun = [Color(0xFF1D3557), Color(0xFF2F5A8F), Colors.white];
  static const _esc = [Color(0xFF173D33), Color(0xFF2B6E5B), Color(0xFF9FE1CB)];
  static const _nav = [Color(0xFF3D3418), Color(0xFF6B5A22), Color(0xFFF3DC8A)];
  static const _fle = [Color(0xFF4A2420), Color(0xFF8A3D34), Color(0xFFFFB4A8)];
  static const _act = [Color(0xFF1F5FBF), Color(0xFF5B9BFF), Colors.white];

  InputModel get inputModel => gFFI.inputModel;

  @override
  void didUpdateWidget(covariant KeyHelpTools oldWidget) {
    super.didUpdateWidget(oldWidget);
    // Si se abre el teclado de letras, el panel se cierra.
    if (widget.keyboardIsVisible && !oldWidget.keyboardIsVisible) {
      _panel = false;
    }
  }

  Widget tecla(String text, List<Color> c, void Function() onPressed,
      {bool active = false,
      IconData? icon,
      double h = 44,
      int flex = 1,
      void Function()? onLongPress}) {
    final col = active ? _act : c;
    return Expanded(
        flex: flex,
        child: Padding(
            padding: EdgeInsets.all(2.5),
            child: SizedBox(
                height: h,
                child: TextButton(
                    style: TextButton.styleFrom(
                      minimumSize: Size(0, 0),
                      padding: EdgeInsets.zero,
                      tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                      backgroundColor: col[0],
                      shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(7.0),
                          side: BorderSide(color: col[1])),
                    ),
                    child: icon != null
                        ? Row(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                                Icon(icon, size: 20, color: col[2]),
                                if (text.isNotEmpty) SizedBox(width: 6),
                                if (text.isNotEmpty)
                                  Text(text,
                                      style: TextStyle(
                                          color: col[2], fontSize: 13)),
                              ])
                        : FittedBox(
                            fit: BoxFit.scaleDown,
                            child: Padding(
                                padding: EdgeInsets.symmetric(horizontal: 3),
                                child: Text(text,
                                    textAlign: TextAlign.center,
                                    style: TextStyle(
                                        color: col[2],
                                        fontSize: 12,
                                        height: 1.1)))),
                    onPressed: onPressed,
                    onLongPress: onLongPress))));
  }

  Widget empty() => Expanded(child: SizedBox());

  Widget chip(String text, bool on, void Function() onPressed,
      {IconData? icon}) {
    return Padding(
        padding: EdgeInsets.only(right: 6),
        child: TextButton(
            style: TextButton.styleFrom(
              minimumSize: Size(0, 0),
              padding: EdgeInsets.symmetric(vertical: 8, horizontal: 12),
              tapTargetSize: MaterialTapTargetSize.shrinkWrap,
              backgroundColor: on ? _act[0] : Color(0xFF23262E),
              shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8.0)),
            ),
            child: Row(mainAxisSize: MainAxisSize.min, children: [
              if (icon != null) Icon(icon, size: 16, color: Colors.white),
              if (icon != null) SizedBox(width: 4),
              Text(text, style: TextStyle(color: Colors.white, fontSize: 13)),
            ]),
            onPressed: onPressed));
  }

  _updateRect() {
    RenderObject? renderObject = _key.currentContext?.findRenderObject();
    if (renderObject == null) {
      return;
    }
    if (renderObject is RenderBox) {
      final size = renderObject.size;
      Offset pos = renderObject.localToGlobal(Offset.zero);
      // Vexly: con el panel abierto la pantalla remota tambien se acomoda arriba.
      final visible = widget.keyboardIsVisible || _panel;
      gFFI.cursorModel.keyHelpToolsVisibilityChanged(
          Rect.fromLTWH(pos.dx, pos.dy, size.width, size.height), visible);
      if (visible && _lastH != size.height) {
        _lastH = size.height;
        gFFI.canvasModel.mobileFocusCanvasCursor();
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final hasModifierOn = inputModel.ctrl ||
        inputModel.alt ||
        inputModel.shift ||
        inputModel.command;

    if (!_panel && !hasModifierOn && !widget.requestShow) {
      _lastH = null;
      gFFI.cursorModel
          .keyHelpToolsVisibilityChanged(null, widget.keyboardIsVisible);
      return Offstage();
    }
    final size = MediaQuery.of(context).size;
    final h = size.width > size.height ? 34.0 : 44.0;

    final pi = gFFI.ffiModel.pi;
    final isMac = pi.platform == kPeerPlatformMacOS;
    final isWin = pi.platform == kPeerPlatformWindows;
    final isLinux = pi.platform == kPeerPlatformLinux;
    final winLinux = isWin || isLinux;
    void k(String name) => inputModel.inputKey(name);

    final ctrl = tecla('Ctrl', _gris, () {
      setState(() => inputModel.ctrl = !inputModel.ctrl);
    }, active: inputModel.ctrl, h: h);
    final alt = tecla('Alt', _gris, () {
      setState(() => inputModel.alt = !inputModel.alt);
    }, active: inputModel.alt, h: h);
    final shift = tecla('Mayús', _gris, () {
      setState(() => inputModel.shift = !inputModel.shift);
    }, active: inputModel.shift, h: h);
    final win = isMac
        ? tecla('Cmd', _gris, () {
            setState(() => inputModel.command = !inputModel.command);
          }, active: inputModel.command, h: h)
        // Vexly: tocar = abre el menu Inicio; dejar pulsado = Win queda
        // presionada (azul) para atajos como Win+R o Win+E.
        : tecla('', _gris, () {
            if (inputModel.command) {
              setState(() => inputModel.command = false);
            } else {
              k('Meta');
            }
          },
            active: inputModel.command,
            icon: Icons.window,
            h: h,
            onLongPress: () =>
                setState(() => inputModel.command = !inputModel.command));

    final top = Row(children: [
      chip(_panel ? 'ABC teclado' : 'Teclas especiales', false, () {
        if (_panel) {
          setState(() => _panel = false);
          widget.openKeyboard();
        } else {
          FocusManager.instance.primaryFocus?.unfocus();
          setState(() => _panel = true);
        }
      }, icon: _panel ? Icons.keyboard : Icons.keyboard_command_key),
      if (_panel) Spacer(),
      if (_panel)
        chip('Ocultar', false, () => setState(() => _panel = false),
            icon: Icons.expand_more),
    ]);

    final List<Widget> rows;
    if (!_panel) {
      // Teclado de letras abierto: solo la fila de modificadores.
      rows = [
        top,
        SizedBox(height: 4),
        Row(children: [ctrl, alt, shift, win, empty(), empty()]),
      ];
    } else {
      rows = [
        top,
        SizedBox(height: 6),
        Row(children: [
          tecla('Esc', _gris, () => k('VK_ESCAPE'), h: h),
          for (var i = 1; i <= 4; ++i)
            tecla('F$i', _fun, () => k('VK_F$i'), h: h),
          tecla('', _esc, () => k('VK_BACK'), icon: Icons.backspace_outlined, h: h),
          tecla('Insert', _nav, () => k('VK_INSERT'), h: h),
          tecla('Inicio', _nav, () => k('VK_HOME'), h: h),
          tecla('Re Pág', _nav, () => k('VK_PRIOR'), h: h),
        ]),
        Row(children: [
          tecla('', _esc, () => k('VK_TAB'), icon: Icons.keyboard_tab, h: h),
          for (var i = 5; i <= 8; ++i)
            tecla('F$i', _fun, () => k('VK_F$i'), h: h),
          tecla('', _esc, () => k('VK_ENTER'),
              icon: Icons.keyboard_return, h: h),
          tecla('Supr', _nav, () => k('VK_DELETE'), h: h),
          tecla('Fin', _nav, () => k('VK_END'), h: h),
          tecla('Av Pág', _nav, () => k('VK_NEXT'), h: h),
        ]),
        Row(children: [
          tecla('Bloq\nMayús', _esc, () => k('VK_CAPITAL'), h: h),
          for (var i = 9; i <= 12; ++i)
            tecla('F$i', _fun, () => k('VK_F$i'), h: h),
          tecla('', _fle, () => k('VK_UP'), icon: Icons.arrow_upward, h: h),
          // to-do: support PrtScr on Mac
          winLinux
              ? tecla('Impr\nPant', _nav, () => k('VK_SNAPSHOT'), h: h)
              : empty(),
          winLinux
              ? tecla('Bloq\nDespl', _nav, () => k('VK_SCROLL'), h: h)
              : empty(),
          winLinux ? tecla('Pausa', _nav, () => k('VK_PAUSE'), h: h) : empty(),
        ]),
        Row(children: [
          shift,
          ctrl,
          alt,
          win,
          tecla('', _fle, () => k('VK_LEFT'), icon: Icons.arrow_back, h: h),
          tecla('', _fle, () => k('VK_DOWN'), icon: Icons.arrow_downward, h: h),
          tecla('', _fle, () => k('VK_RIGHT'), icon: Icons.arrow_forward, h: h),
          winLinux ? tecla('Menú', _gris, () => k('Apps'), h: h) : empty(),
          empty(),
        ]),
        Row(children: [
          tecla('Copiar', _gris, () => sendPrompt(isMac, 'VK_C'),
              icon: Icons.copy, h: h, flex: 3),
          tecla('Pegar', _gris, () => sendPrompt(isMac, 'VK_V'),
              icon: Icons.paste, h: h, flex: 3),
          tecla('Guardar', _gris, () => sendPrompt(isMac, 'VK_S'),
              icon: Icons.save_outlined, h: h, flex: 3),
        ]),
      ];
    }

    // 500 ms is long enough for this widget to be built!
    Future.delayed(Duration(milliseconds: 500), () {
      _updateRect();
    });
    return Positioned(
        left: 0,
        right: 0,
        bottom: 0,
        child: Container(
            key: _key,
            color: Color(0xF0111318),
            padding: EdgeInsets.fromLTRB(6, 6, 6, 8),
            child: SafeArea(
                top: false,
                child: Column(mainAxisSize: MainAxisSize.min, children: rows))));
  }
}
""" + "\n" + s[fin:]
s = s.replace(viejo, """            KeyHelpTools(
                keyboardIsVisible: keyboardIsVisible,
                showGestureHelp: _showGestureHelp,
                openKeyboard: openKeyboard),""")
open(p, "w", encoding="utf-8").write(s)

# El panel va abajo (encima del teclado), no arriba: la pantalla remota
# se achica por la altura del panel y ya no se corre hacia abajo.
m = "flutter/lib/models/model.dart"
t = open(m, encoding="utf-8").read()
a = """          (parent.target?.cursorModel.keyHelpToolsRectToAdjustCanvas?.bottom ??
              0);"""
b = """    final bottom =
        parent.target?.cursorModel.keyHelpToolsRectToAdjustCanvas?.bottom ?? 0;
    return max(bottom - MediaQueryData.fromView(ui.window).padding.top, 0);"""
assert t.count(a) == 1 and t.count(b) == 1, "model.dart cambio; revisar el panel de teclas"
t = t.replace(a, """          (parent.target?.cursorModel.keyHelpToolsRectToAdjustCanvas?.height ??
              0);""")
t = t.replace(b, """    return 0.0;""")
open(m, "w", encoding="utf-8").write(t)
print("Panel de teclas aplicado")
