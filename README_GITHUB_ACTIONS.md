
Analista Esportivo - CI-ready project
===================================

Passos para gerar APK via GitHub Actions (recomendado):
1. Crie um repositório novo no GitHub (p.ex. analista-esportivo-pro).
2. Faça upload do conteúdo deste zip (tudo), commit e push para a branch 'main'.
3. Vá em Actions no GitHub e execute o workflow 'Build APK with Buildozer' ou aguarde o push.
4. Após a execução, acesse a aba 'Artifacts' do job e baixe o arquivo .apk/.aab gerado.

Observações:
- A build do Android é pesada e pode falhar sem ajustes finos de dependências nativas.
- Se houver erros, cole os logs aqui que eu te ajudo a ajustar o workflow/buildozer.spec.
