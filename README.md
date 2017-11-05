# dropboxSO
Cloud storage system - Operational Systems Project

# IMPORTANT: There are no authentication nor identity-related security measures implemented

Basic functionality includes:
* Uploads and Downloads files/directories and monitors changes in the chosed directory

* Detects items in conflict and creates a backup copy denoting the problem.
    Conflicts happen as follows:
    1.Client A and Client B have and item X synchronized
    2.Both clients go offline
    3.Both clients modify item X
    4.Client A goes online and synchronizes with the server
    5.Client B goes online -> Conflict

    In summary, a conflict is detected when:
    A. The item on the server is more recent then the local copy
    B. The server modification time is less than the current login time (this is when we logged back in and there were already files on the server)
    C. A file modification has happened after a client's last logout (this is when we modified a file after logging out and before logging in)


