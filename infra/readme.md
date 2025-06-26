# Considerações Importantes
Para que sua aplicação funcione corretamente com Graviton2, você precisa garantir que:

Imagem Docker Multi-Arquitetura (ou ARM64 Específica): Sua imagem Docker (gerada pelo Dockerfile) precisa ser compatível com a arquitetura ARM64.

Imagens Base: Se você estiver usando imagens base como python:3.9-slim-buster, elas geralmente já são multi-arquitetura (contêm versões para x86 e ARM64). Você pode verificar isso com docker pull --platform linux/arm64 python:3.9-slim-buster.
Compilação: Ao construir sua imagem Docker no ambiente de desenvolvimento, se seu ambiente for x86 (a maioria dos laptops), você precisará usar o Buildx para construir a imagem especificamente para a plataforma ARM64.
