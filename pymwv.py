"""MIT License

Copyright (c) 2018 Mauricio Carvalho Mathias de Paulo

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE."""
from osgeo import ogr
import math, sys

class MWVD():
    def ApoloniusCircle(self,s1,s2,w1,w2,  extent): #ogrpoint s1,s2, double w1,w2
        #Aurenhammer's formulae
        s1x=s1.GetX()
        s1y=s1.GetY()
        s2x=s2.GetX()
        s2y=s2.GetY()
        if(w1==w2): #regular voronoi
            mx=(s1x+s2x)/2.
            my=(s1y+s2y)/2.
            dx=s1x-s2x
            dy=s1y-s2y
            d=extent.GetBoundary().Length()
            curve=ogr.Geometry(ogr.wkbLineString)
            
            if (dy!=0):
                m=math.atan(-1.*(dx/dy))
                curve.AddPoint_2D(-d*math.cos(m)+mx,-d*math.sin(m)+my)
                curve.AddPoint_2D(d*math.cos(m)+mx,d*math.sin(m)+my)
            else:
                curve.AddPoint_2D(mx,-d+my)
                curve.AddPoint_2D(mx,d+my)
            b=extent.GetBoundary()
            shortCurve=curve.Intersection(extent)
            diff=b.Difference(curve)
            boundary=diff.GetGeometryRef(1)
            endPoint=boundary.GetPoint(0)
            boundary.AddPoint_2D(endPoint[0],  endPoint[1])
            ring=ogr.Geometry(ogr.wkbLinearRing)
            for point in boundary.GetPoints():
                ring.AddPoint_2D(point[0],  point[1])
            ring.AddGeometry(boundary)
            domBoundary=ogr.Geometry(ogr.wkbPolygon)
            domBoundary.AddGeometry(ring)
            
        else: #weighted voronoi
            den=1./(w1*w1-w2*w2);
            cx=(w1*w1*s2x-w2*w2*s1x)*den
            cy=(w1*w1*s2y-w2*w2*s1y)*den
            #print('Center:', cx, cy)
            d= math.sqrt(((s1x-s2x)*(s1x-s2x) + (s1y-s2y)*(s1y-s2y)))
            r=w1*w2*d*den
            #print("Radius:",r)
            if (r<0): r=r*-1
            #creating the circle boundary from 3 points
            arc= ogr.Geometry(ogr.wkbCircularString) 
            arc.AddPoint_2D(cx+r,cy)
            arc.AddPoint_2D(cx-r,cy)
            arc.AddPoint_2D(cx+r,cy)
            #creating the circle polygon
            domBoundary=ogr.Geometry(ogr.wkbCurvePolygon)
            domBoundary.AddGeometry(arc)
        if s1.Intersects(domBoundary):
            return domBoundary.Intersection(extent)
        else:
            return extent.Difference(domBoundary)
    def getMWVLayer(self,  sites,  outDS,  layerName, extent):
        outLayer = outDS.CreateLayer(layerName, geom_type=ogr.wkbPolygon )
        for site1 in sites:
            dominance=extent
            for site2 in sites:
                if site1!=site2:
                    twoSitesDominance=self.ApoloniusCircle(site1['p'], site2['p'], site1['w'], site2['w'], extent)
                    dominance=dominance.Intersection(twoSitesDominance)
            # Get the output Layer's Feature Definition
            featureDefn = outLayer.GetLayerDefn()
            # create a new feature
            outFeature = ogr.Feature(featureDefn)
            # Set new geometry
            outFeature.SetGeometry(dominance.GetLinearGeometry())
            # Add new feature to output Layer
            outLayer.CreateFeature(outFeature)
            
    def readSitesFromLayer(self, ds, layerName, weightAttribute):
        layer=ds.GetLayerByName(layerName)
        sites=[]
        for feature in layer:
            w=feature.GetFieldAsDouble(weightAttribute)
            p=feature.GetGeometryRef()
            sites.append({'p':p.Clone(),  'w':w})
        return sites
            
    def getLayerExtent(self, ds,  layerName):
        layer=ds.GetLayerByName(layerName)
        extent=ogr.Geometry( ogr.wkbPolygon)
        lring=ogr.Geometry( ogr.wkbLinearRing)
        le=layer.GetExtent()
        lring.AddPoint(le[0], le[0])
        lring.AddPoint(le[0], le[3])
        lring.AddPoint(le[1], le[3])
        lring.AddPoint(le[1], le[0])
        lring.AddPoint(le[0], le[0])
        extent.AddGeometry(lring)
        d=abs(le[0]-le[2])
        extent=extent.Buffer(d/10., 0)
        return extent
        

if __name__=="__main__":
    if (len(sys.argv) !=5):
        print("USAGE:")
        print("python pymwv.py ogrDataSource SitesLayerName WeightAttribute OutpuLayerName")
    else:
        runObj=MWVD()
        outDS=ogr.Open(sys.argv[1], 1)
        sites=runObj.readSitesFromLayer(outDS, sys.argv[2], sys.argv[3])
        extent=runObj.getLayerExtent(outDS,  sys.argv[2])
        runObj.getMWVLayer(sites, outDS, sys.argv[4], extent)
 

