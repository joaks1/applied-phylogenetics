usage="sh pandoc.sh input.md output.pdf"
if [ $# -ne 2 ]
then
    echo "usage: $usage"
    exit 0
fi

pandoc -t beamer -s "${1}" -o "${2}" --slide-level=1 -V theme:boxes -V colortheme:seahorse

