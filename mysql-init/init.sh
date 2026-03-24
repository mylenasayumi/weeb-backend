#!/bin/bash
mysql -u root -p"${MYSQL_ROOT_PASSWORD}" <<EOF
GRANT ALL PRIVILEGES ON \`test\_%\`.* TO '${MYSQL_USER}'@'%';
FLUSH PRIVILEGES;
EOF