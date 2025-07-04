# Guia de Contribuição para o Hephaestus Agent

Primeiramente, obrigado por considerar contribuir para o Hephaestus Agent! Estamos animados em ver o interesse da comunidade. Este documento fornece diretrizes para contribuir com o projeto.

## Como Contribuir

Acolhemos diversos tipos de contribuições, incluindo, mas não se limitando a:

*   Correções de bugs
*   Desenvolvimento de novas funcionalidades (conforme o `ROADMAP.md` ou novas ideias)
*   Melhorias na documentação
*   Envio de issues (relatos de bugs ou sugestões de funcionalidades)
*   Feedback sobre o projeto

### Relatando Bugs ou Sugerindo Melhorias

*   Utilize a seção "Issues" do nosso repositório no GitHub.
*   Antes de criar uma nova issue, por favor, verifique se já não existe uma similar.
*   Para bugs, forneça o máximo de detalhes possível:
    *   Passos para reproduzir o bug.
    *   Comportamento esperado vs. comportamento observado.
    *   Versão do Python, sistema operacional.
    *   Logs relevantes (de `hephaestus.log`) ou tracebacks de erro.
*   Para sugestões de funcionalidades, descreva claramente a funcionalidade proposta e por que ela seria útil.

### Processo de Desenvolvimento e Pull Request

1.  **Fork o Repositório (se aplicável):**
    Se estiver trabalhando com um repositório Git remoto central (ex: no GitHub, GitLab), crie um fork do repositório principal para sua conta pessoal. Para desenvolvimento puramente local, este passo não é necessário.

2.  **Clone seu Repositório/Fork:**
    Clone o repositório para sua máquina local.
    ```bash
    git clone [URL_DO_SEU_REPOSITORIO_OU_FORK]
    cd hephaestus-agent # Ou o nome do diretório do seu projeto
    ```

3.  **Crie uma Branch:**
    Crie uma branch descritiva para sua feature ou correção:
    ```bash
    git checkout -b minha-nova-feature # Ex: feature/adicionar-nova-ferramenta
    # ou
    git checkout -b correcao-bug-x # Ex: fix/corrigir-erro-validacao
    ```

4.  **Faça suas Alterações:**
    *   Escreva um código claro e conciso.
    *   Siga as convenções de estilo Python (PEP 8).
    *   Adicione ou atualize a documentação relevante (docstrings, arquivos `.md`) conforme necessário.

5.  **Escreva Testes:**
    *   Novas funcionalidades devem incluir testes unitários ou de integração.
    *   Correções de bugs idealmente devem incluir um teste que demonstre o bug e verifique a correção.
    *   Execute todos os testes para garantir que nada foi quebrado:
        ```bash
        pytest
        ```

6.  **Faça o Commit das suas Alterações:**
    *   Use mensagens de commit claras e descritivas. Recomendamos seguir o padrão [Conventional Commits](https://www.conventionalcommits.org/).
    *   Exemplo: `git commit -m "feat: Adiciona nova ferramenta de análise de X"`
    *   Exemplo: `git commit -m "fix: Corrige erro de validação em Y ao processar Z"`

7.  **Envie para seu Fork:**
    ```bash
    git push origin minha-nova-feature
    ```

8.  **Abra um Pull Request (PR):**
    *   Se estiver usando um servidor Git remoto, navegue até o repositório original e crie um Pull Request a partir da sua branch.
    *   Preencha o template do PR com uma descrição clara das suas alterações, o que o PR resolve (ex: "Closes #123", se estiver usando um sistema de issues), e quaisquer notas relevantes para os revisores.
    *   Certifique-se de que seu PR tem como alvo a branch principal do repositório.

### Revisão do Código
*   Se houver outros colaboradores ou um processo de revisão, seu PR será revisado.
*   Esteja aberto a feedback e discussões construtivas.
*   Faça as alterações solicitadas em sua branch e envie-as novamente (o PR será atualizado automaticamente).
*   Uma vez que o PR for aprovado e os testes passarem, ele será mesclado.

## Diretrizes Adicionais

*   **Código de Conduta:** Ao contribuir, você concorda em seguir nosso [Código de Conduta](CODE_OF_CONDUCT.md).
*   **Comunicação:** Para discussões mais amplas sobre o projeto ou ideias, considere abrir uma "Discussion" no GitHub (se habilitado) ou entrar em contato com os mantenedores.
*   **Licença:** Ao contribuir com código, você concorda em licenciar sua contribuição sob os termos da licença do projeto (verifique o arquivo `LICENSE` - se não existir, este é um bom momento para adicionar um!).

Obrigado novamente por seu interesse em contribuir!
