# Vexly: Apple (ITMS-91061) pide "privacy manifest" en 7 librerias.
# Se suben a las primeras versiones que lo traen. Se aplica al compilar
# (tiendas-ios.yml); no se guarda en el codigo de Canela.
import re
import subprocess

p = "flutter/pubspec.yaml"
s = open(p, encoding="utf-8").read()
nuevas = {
    "file_picker": "^8.0.0",         # 8.0.0 trae PrivacyInfo.xcprivacy
    "device_info_plus": "^10.1.2",   # 10.0.1 lo trae (10.0.0 fue retirada)
    "package_info_plus": "^8.0.0",   # 6.0.0 lo trae
    "sqflite": "^2.3.1",             # 2.3.1 lo trae
}
for nombre, version in nuevas.items():
    s, n = re.subn(r"(?m)^  " + nombre + r": .*$", "  " + nombre + ": " + version, s)
    assert n == 1, "no encontre " + nombre + " en pubspec.yaml"
open(p, "w", encoding="utf-8").write(s)
subprocess.run(["flutter", "pub", "upgrade"] + list(nuevas), cwd="flutter", check=True)

# Librerias de iOS que vienen con file_picker: primeras versiones con manifiesto.
m = "flutter/ios/Podfile"
t = open(m, encoding="utf-8").read()
a = "  flutter_install_all_ios_pods File.dirname(File.realpath(__FILE__))\n"
assert t.count(a) == 1, "Podfile cambio; revisar"
t = t.replace(a, a + """  pod 'DKImagePickerController/PhotoGallery', '>= 4.3.9'
  pod 'DKPhotoGallery', '>= 0.0.19'
  pod 'SwiftyGif', '>= 5.4.5'
""")
open(m, "w", encoding="utf-8").write(t)
print("Manifiestos de privacidad: librerias actualizadas")
