conda config --add channels conda-forge

conda create -y -n openmc-env
conda activate openmc-env

sudo conda install -y mamba

mamba search openmc
sudo mamba install -y openmc

sudo conda install -y -n openmc-env ipykernel

hdf5_file_name=jeff33.tar.xz
hdf5_data_path=~/nuclear_data/hdf5
mkdir -p $hdf5_data_path
curl -L -o $hdf5_file_name https://anl.box.com/shared/static/4jwkvrr9pxlruuihcrgti75zde6g7bum.xz
tar -xvf $hdf5_file_name -C $hdf5_data_path
rm $hdf5_file_name

chain_file_name=chain_casl_pwr.xml
chain_data_path=~/nuclear_data/hdf5/simplified_chain
mkdir -p $chain_data_path
curl -L -o $chain_file_name https://anl.box.com/shared/static/nyezmyuofd4eqt6wzd626lqth7wvpprr.xml
mv $chain_file_name $chain_data_path

echo export OPENMC_CROSS_SECTIONS="$hdf5_data_path/jeff-3.3-hdf5/cross_sections.xml">>~/.zshrc
echo export OPENMC_DEPLETION_CHAIN="$chain_data_path/$chain_file_name">>~/.zshrc
