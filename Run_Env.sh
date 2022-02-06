if [ "$#" -eq "0" ]
then
    me="$(basename "$(test -L "$0" && readlink "$0" || echo "$0")")"
    echo "Usage on this script ${me} [-n|-a|-0]"
    echo ""
    echo "workspace   Open folders in workspaces"
    echo "remote      Open folders in VSCode-remote"
    echo "none        Only build without open VSCode"
fi

if [ "$#" -eq "1" ] 
then
    docker-compose build
    docker-compose up -d

    cp -r ./docker/musician ./src
    cp -r ./docker/orchestra ./src

    docker-compose exec dj-musician bash ./.devcontainer/setup.sh
    docker-compose exec dj-orchestra bash ./.devcontainer/setup.sh

    if [ "$1" == "remote" ]
    then
        code -n ./src/musician && code -n ./src/orchestra
    fi

    if [ "$1" == "workspace" ]
    then
        code -a ./src/musician/django-musician && code -a ./src/orchestra
    fi
fi

