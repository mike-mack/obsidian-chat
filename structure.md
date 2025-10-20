obsidian-chat/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── db/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── session.py
│   │   └── alembic/...
│   ├── services/
│   │   ├── vault_manager.py
│   │   ├── file_parser.py
│   │   ├── chunker.py
│   │   ├── embedder/
│   │   │   ├── base.py
│   │   │   ├── openai_impl.py
│   │   │   └── local_impl.py
│   │   ├── vectorstore.py
│   │   └── query_engine.py
│   ├── api/
│   │   ├── routes_vaults.py
│   │   └── routes_query.py
│   └── templates/
│       ├── index.html
│       ├── vaults_list.html
│       └── query.html
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
└── README.md