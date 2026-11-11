# Ferramentas do site projeto3d-hpb

## Abas 3D
1. `python3 tools/glue.py tools/fontes/mapa3d_HPB_vNN.html` → `private/full.html` (aba 3D HPB Completa) e `private/full_info.html` (notas para a aba Informação).
2. `python3 tools/rec_build.py tools/fontes/<base_3D_do_reparos>.html tools/fontes/mapa3d_reparos_HPB_v1-04.11.2026.html` → `private/rec.html` (aba Recomendações) = `full.html` atual + módulo "Reparos do report" + dados do report mais recente (`tools/out/rep_<N>.json`) + fotos "depois".
3. `python3 tools/acomp_build.py CRONOGRAMA.xml` → `private/acomp.html` (aba Acompanhamento) = `full.html` atual restrito ao conjunto Fornalha + andamento do overhaul lido do cronograma MS Project (XML). As tarefas são achadas pelo nome (câmaras C1–C6, Fase 02, paredes 25k, divisórias, tubos do piso); o script avisa "NAO ENCONTRADO" se algum nome mudar. Sem o XML, reaproveita `tools/out/acomp_tasks.json`.
   O passo 1 também gera `public/fluxos.html` (link aberto, sem login: **/fluxos**), só com o 3D + os fluxos da caldeira (`tools/fluxos3d.html`: água, vapor, ar, gases, sólidos, calcário/areia e cinzas correndo dentro do modelo, com Raio‑X e modo leve), já ligados. O `full.html` do site não recebe o módulo. Os trajetos ficam em coordenadas do mapa (T, d, El em metros); os assumidos levam `assumed:1` e aparecem com anéis laranja / linha tracejada.
   Sempre que o 3D HPB Completa mudar, rode os três passos (Recomendações e Acompanhamento usam o mesmo modelo 3D).
   Para atualizar só o andamento: exporte o cronograma do Project em XML e rode apenas o passo 3.

## Reports de inspeção (aba Recomendações)
- `python3 tools/rep_report.py REPORT.pdf [--dry-run]` → lê o PDF, localiza cada recomendação no 3D, recorta fotos antes/depois para `private/rep_img/`, grava `tools/out/rep_<N>.json` e `tools/out/localizacao_<N>.tsv` (origem e confiança de cada item) e atualiza `private/rec.html`.
- `python3 tools/rep_aprender.py N 'LOC_JSON' "Zona" [--regra 'regex'] [--fora "motivo"]` → corrige/confirma a posição de um item e grava na base `tools/rep_locais.json` (memória + regras + histórico). Próximos reports usam o que foi aprendido.
- Foto "depois" enviada fora do PDF: salvar em `tools/rep_depois/r<REPORT>_dep_<N>.jpg` e rodar `python3 tools/rep_patch.py`.

Ordem de localização: memória confirmada > texto explícito do report (divisória/parede, tubos, elevação) > memória automática > regras por palavra-chave > "Local não identificado".
