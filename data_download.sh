# files will be stored in data directory
data_dir="./data"
mkdir -p "$data_dir"

# Download files using gdown
gdown --fuzzy 'https://drive.google.com/file/d/1QbT5FDOJtdVd7AqZ-ekwUh2_pn6nNpb3/view' -O "$data_dir/output_pred21_8_30.zip"
gdown --fuzzy 'https://drive.google.com/file/d/1UTPGv8QUgqSVQ2JeX9QVW0YhbGRxONLL/view' -O "$data_dir/wiki-news-300d-1M.zip"

# Unzip the files
unzip "$data_dir/output_pred21_8_30.zip" -d "$data_dir"
rm "$data_dir/output_pred21_8_30.zip" # Remove the zip file

unzip "$data_dir/wiki-news-300d-1M.zip" -d "$data_dir"
rm "$data_dir/wiki-news-300d-1M.zip" # Remove the zip file

# Local or Docker mode handling

# Copy word embeddings
word_embedding_path="word_embedding/data"
mkdir -p "$word_embedding_path"
cp "$data_dir/wiki-news-300d-1M.txt" "$word_embedding_path"

# Copy KGQAN model files
kgqan_model_path="src/kgqan/model/"
mkdir -p "$kgqan_model_path"
cp -r "$data_dir/output_pred21_8_30/"* "$kgqan_model_path"
