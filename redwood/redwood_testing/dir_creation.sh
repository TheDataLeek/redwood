rm -r ./trash
mkdir ./trash
mkdir level0
cd level0
touch a b c d e f
touch -t 0303031235 b d f
mkdir level1a
mkdir level1b
mkdir level1c
cd level1a
touch g h i j k
touch -t 0303031235 h k
cd ../level1c
touch l m n
touch -t 0303031235 l m n
cd ../level1b
touch o p q
touch -t 0303031235 q
cd ..
mkdir empty
