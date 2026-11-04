# Ferramentas do site projeto3d-hpb

## Abas 3D
1. `python3 tools/glue.py tools/fontes/mapa3d_HPB_vNN.html` → `private/full.html` (aba 3D HPB Completa) e `private/full_info.html` (notas para a aba Informação).
2. `python3 tools/rec_build.py tools/fontes/<base_3D_do_reparos>.html tools/fontes/mapa3d_reparos_HPB_v1-04.11.2026.html` → `private/rec.html` (aba Recomendações) = `full.html` atual + módulo "Reparos do report" + dados do report mais recente (`tools/out/rep_<N>.json`) + fotos "depois".
   Sempre que o 3D HPB Completa mudar, rode os dois passos (a aba Recomendações usa o mesmo modelo 3D).

## Reports de inspeção (aba Recomendações)
- `python3 tools/rep_report.py REPORT.pdf [--dry-run]` → lê o PDF, localiza cada recomendação no 3D, recorta fotos antes/depois para `private/rep_img/`, grava `tools/out/rep_<N>.json` e `tools/out/localizacao_<N>.tsv` (origem e confiança de cada item) e atualiza `private/rec.html`.
- `python3 tools/rep_aprender.py N 'LOC_JSON' "Zona" [--regra 'regex'] [--fora "motivo"]` → corrige/confirma a posição de um item e grava na base `tools/rep_locais.json` (memória + regras + histórico). Próximos reports usam o que foi aprendido.
- Foto "depois" enviada fora do PDF: salvar em `tools/rep_depois/r<REPORT>_dep_<N>.jpg` e rodar `python3 tools/rep_patch.py`.

Ordem de localização: memória confirmada > texto explícito do report (divisória/parede, tubos, elevação) > memória automática > regras por palavra-chave > "Local não identificado".
