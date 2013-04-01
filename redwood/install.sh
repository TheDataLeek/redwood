BASHSCAN=`grep -e "export PATH=\$PATH:\$HOME/bin" $HOME/.bashrc`
if [ -d "$HOME/bin" ]; then
    if [ -f $HOME/.bashrc ]; then
        echo export PATH=$PATH:$HOME/bin >> $HOME/.bashrc
    else
        echo export PATH="$PATH:$HOME/bin" > $HOME/.bashrc
    fi
else
    mkdir $HOME/bin
fi
cp -v ./redwood.py $HOME/bin/redwood
cp -v ./.redwoodrc $HOME/
source $HOME/.bashrc
