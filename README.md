# pymwv
Python Multiplicatively Weighted Voronoi (Diagram)

- Hello
Thank you for your interest in this small piece of code. GDAL has evolved a lot in the past years so now it's pretty easy to implement a Multiplicatively Weighted Voronoi Diagram, unlike when I was pursuing my Masters Degree. So here it is.

- Requirements:  
python3-gdal

- Usage:
```bash
python pymwv.py ogrDataSource SitesLayerName WeightAttribute OutpuLayerName
```

The program will create a new layer on the same ogrDataSource. I hope that this piece of code will be usefull for you.

- Example:  
```bash
unzip test_data.zip  
python pymwv.py ./test_data test_data weight out_data
```

- Colab Notebook
We added a colab notebook that uses data from a list of sites and weights to show the class working. Thanks micycle1.
[Link to the notebook](https://github.com/mauriciodev/pymwv/blob/master/pymwv.ipynb)
