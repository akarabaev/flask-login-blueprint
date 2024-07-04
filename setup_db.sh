if [ -d "migrations" ]; then
    echo "Directory 'migrations' exists. Removing it"
    rm -r migrations
fi

if [ -f "app.db" ]; then
    echo "File 'app.db' exists. Removing it"
    rm app.db
fi


flask db init
flask db migrate -m "Initial migration"
flask db upgrade
