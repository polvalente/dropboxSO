# dropboxSO
Cloud storage system - Operational Systems Project

# IMPORTANT: There are no authentication nor identity-related security measures implemented

# Project Proposal
The proposed project is a cloud storage service. The minimum viable product (MVP) architecture consists of a single server, which allows multiple access through different instances of client application.
The server will be a Web server with API REST. The client application doesn’t have a defined architecture yet, but, in addition to communicating with the server, it will provide a configuration interface for the user. For MVP, multiple user accounts don’t need to be implemented.

# Requirements
The synchronization and consistence between the server and the clients must be guaranteed. Moreover, the system must detect and warn the user when conflicts exists. A conflict occurs when two clients modify a same file at different times.

# Conflict Detection
A conflict occurs when the following sequence of events occurs:
1) Clients A  B have a file X synchronized;
2) Both clients go off-line;
3) Both clients make distinct modifications to file X;
4) Client A go online and synchronizes as usual;
5) Client B go online. Now there is a conflict.

# Implementation
The system comes up with a star-shaped network architecture, with each client communicating with the server. Because of this, it was chosen to leave the greater workload in the client applications as well as the conflict detection.
Client
At the client, the 'update' function is the system brain, tagging the files to make the decisions accordingly. Besides, it is at the client that conflict resolution occurs, in wihich a copy of the local file is created with another name before downloading the conflicting file from the server.

# Server
The server is implemented in Flask because it is a library that provides a simple way to create a Web interface in which client applications can communicate with the server
## Server API

### /\<user\>/download:
Sends the required file, whose name is received in the body of the POST request. Sending is done through the ‘send_file’ function provided by the Flask library.
    
### /\<user\>/upload/\<ftype\>:
It receives the contents and file name in the file parameter sent in the POST request and, by URL, receives the file type (file or directory). If it is a directory, nothing is received and create the corresponding directory is enough.
Recebe o conteúdo e o nome do arquivo no parâmetro de arquivos enviados na requisição POST e, pela URL, recebe o tipo de arquivo (se é arquivo ou diretório). Caso seja um diretório, nada é recebido e basta criar o diretório correspondente.

### /\<user\>/delete:
Removes the specified file in the body of the POST request, receiving the name and type of the file (file or directory) in 'name' and 'type' parameters.

### /\<user\>/list:
Returns a data structure relative to the files list at the server. For each file, this structure stores the level, which is related to its depth in the file tree and its modification date (UNIX time)

# Client

The client is an application which makes HTTP requests according to the API described above. The conflict resolution is implemented here, through the main functions <i>update</i> and <i>decide</i>.
