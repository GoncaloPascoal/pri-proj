# PRI Project
Repository for the Information Processing and Retrieval project, focused on the development of a search system for Steam games.

## Usage

```bash
docker run --name pri -p 8983:8983 solr:8.10
make solr cn=pri
```

http://localhost:8983/solr/#/games/query
