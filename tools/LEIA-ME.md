# Geração das abas 3D

1. `python3 glue.py mapa3d_HPB_vNN.html` → gera `private/full.html` (aba 3D HPB Completa) e `private/full_info.html` (notas para a aba Informação).
2. `python3 rec_build.py <base_3D_usada_pelo_reparos.html> <mapa3d_reparos_vN.html>` → gera `private/rec.html` (aba Recomendações) = `full.html` atual + módulo "Reparos do report".

Sempre que o 3D HPB Completa mudar, rode os dois passos: a aba Recomendações usa sempre o mesmo modelo 3D.
(Os caminhos SC/R dentro dos scripts apontam para o ambiente onde foram usados; ajuste se rodar em outro lugar.)
3. `rec_build.py` já chama `rep_patch.py`, que coloca as fotos "depois" de `tools/rep_depois/dep_<n>.jpg` (recortadas do PDF do report) e tira o botão "Anexar foto".
