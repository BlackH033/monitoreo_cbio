
from array import array
import rasterio as rs
import matplotlib.pyplot as plt
import numpy as np
from rasterio import plot
import os
from windows import *
from shapely.geometry import shape
import rasterio
import geopandas as gpd
from datetime import datetime
from rasterio.features import geometry_mask
#--------------------------------------------------
class procesamiento():
    carpeta_raiz=os.path.dirname(__file__)          #guarda la ruta donde se encuentra este archivo .py
    carpeta_img=os.path.join(carpeta_raiz,"img")    #crea la ruta relativa a la carpeta /img - la cual se guarda en la misma ruta del archivo .py
    ruta=""
    def __init__(self,ruta,tipo):
        super().__init__()
        self.ruta=ruta
        self.directorio=os.listdir(ruta)
        print(self.ruta)
        #funciones

        #ndvi=(nir-red)/(nir+red)
        def ndvi(red,nir):
            #ndvi=np.where((nir+red)==0,0,(nir-red)/(nir+red))
            return (nir-red)/(nir+red)

        def verdadero_color(r,g,b):
            r=r/r.max()
            g=g/g.max()
            b=b/b.max()
            rgb=np.dstack((r,g,b))
            return rgb

        def porcentaje(x,años):
            if len(x)==1:return "Año inicial"
            else:
                porc=(x[-1]-x[-2])/x[-2]*100
                if porc>0:return f"Incremento del {round(porc,3)}% con\nrespecto al año {años[-2]}"
                else:return f"Decremento del {round(porc,3)}% con\nrespecto al año {años[-2]}"

        def info(ax,x,m):
            ax.text(0.5, 0.95, f"Pixeles totales: {x.size}", ha='center', va='center', fontsize=12, color='black')
            ax.text(0.5, 0.9, f"Dimensión: {x.shape}", ha='center', va='center', fontsize=12, color='black')
            ax.text(0.5, 0.8, f"Valor NDVI minimo: {round(np.nanmin(x),3)}", ha='center', va='center', fontsize=12, color='black')
            ax.text(0.5, 0.75, f"Valor NDVI maximo: {round(np.nanmax(x),3)}", ha='center', va='center', fontsize=12, color='black')
            ax.text(0.5, 0.7, f"Valor NDVI promedio: {round(np.nanmean(x),3)}", ha='center', va='center', fontsize=12, color='black')
            ax.text(0.5, 0.65, f"_______________________________________", ha='center', va='center', fontsize=12, color='black')
            ax.text(0.5, 0.5, m, ha='center', va='center', fontsize=12, color='black')
            #ax.text(0.5, 0.6, f"", ha='right', va='center', fontsize=12, color='black')
            #ax.text(0.5, 0.6, f"", ha='right', va='center', fontsize=12, color='black')
            #ax.text(0.5, 0.6, f"", ha='right', va='center', fontsize=12, color='black')
            salida1=f"Pixeles totales: {x.size} |  |  | | "
            #plt.figtext(0.05,0.05,salida1, bbox = {'facecolor': 'oldlace', 'alpha': 0.5, 'boxstyle': "square,pad=0.3", 'ec': 'black'})

        def clas(x):
            if 0.6<x<=1:return 0
            elif 0.4<x<=0.6:return 1
            elif 0.2<x<=0.4:return 2
            elif -1<=x<=0.2:return 3

        def cambio2(x,y):
            global factor
            factor=np.array([[None,1   ,2   ,3],
                            [4   ,None,5   ,6],
                            [7   ,8   ,None,9],
                            [10  ,11  ,12  ,None]])
            return factor[x][y]

        def listar_tif(x):
            return [i for i in x if i[-4:]==".tif"]

        def crear_carpeta(ruta):
            conteo=1
            if "resultado" in self.directorio:
                while True:
                    if f"resultado ({conteo})" not in self.directorio:
                        os.mkdir(os.path.join(ruta,f"resultado ({conteo})"))
                        return os.path.join(ruta,f"resultado ({conteo})")
                    conteo+=1
            else:
                os.mkdir(os.path.join(ruta,"resultado"))
                return os.path.join(ruta,"resultado")
        
        def guardar_ndvi(ruta,tiffs,data,crs,width,height,transform):
            print(tiffs)
            os.mkdir(os.path.join(ruta,"geotiff"))
            ruta=os.path.join(ruta,"geotiff")
            for i in range(len(data)):
                ndviImage = rs.open(os.path.join(ruta,f"NDVI_{tiffs[i]}"), 'w', driver='Gtiff',
                        width=width, height=height,
                        count=1,
                        crs=crs,
                        transform=transform,
                        dtype='float64'                  
                        )
                ndviImage.write(data[i],1) #ndvi
                ndviImage.close()
        
        def mostrar_ndvi_individual(ruta,names,ndvi,tipo):
            nombre=ruta.split("/")
            nombre=nombre[-1].split("\\")
            prom=[]
            años=[]
            #plt.ion()
            os.mkdir(os.path.join(ruta,"graficos"))
            for i in range(len(names)):  
                prom.append(round(np.nanmean(ndvi[i]),3))
                años.append(names[i][:-4])
                fig = plt.figure(figsize=(14,6))
                gs = fig.add_gridspec(1, 2, width_ratios=[2, 1]) 
                ax = fig.add_subplot(gs[0]) 
                ax2 = fig.add_subplot(gs[1]) 
                im = ax.imshow(ndvi[i], cmap='RdYlGn',vmax=1)
                plt.colorbar(im, ax=ax,label='NDVI')
                fig.suptitle(f'Índice de Vegetación de Diferencia Normalizada (NDVI) para {names[i][:-4]} en {nombre[0]}',weight='bold',size=16)
                ax.axis('off')
                info(ax2,ndvi[i],porcentaje(prom,años))
                ax2.set_xlim(0, 1)
                ax2.set_ylim(0, 1)
                ax2.set_xticks([])
                ax2.set_yticks([])

                inner_left = 0.6658
                inner_bottom = 0.1
                inner_width = 0.234#5
                inner_height = 0.3
                inner_ax = fig.add_axes([inner_left, inner_bottom, inner_width, inner_height])
                inner_ax.hist(ndvi[i].flatten(),label="NDVI",color="green",bins=200,range=(-1,1))   
                if tipo==1:
                    plt.get_current_fig_manager().window.state('zoomed')
                    plt.show()
                fig.savefig(os.path.join(os.path.join(ruta,f"graficos"),f"visual_NDVI_{names[i][:-4]}.png"), dpi=300,bbox_inches='tight')
                plt.close(fig)
            #plt.ion()
            
            for i in range(len(names)):
                fig, ax = plt.subplots()
                im = ax.imshow(ndvi[i], cmap='RdYlGn',vmax=1)
                fig.colorbar(im, ax=ax,label='NDVI')
                plt.axis('off')
                plt.ioff()
                plt.savefig(os.path.join(os.path.join(ruta,f"graficos"),f"grafico_NDVI_{names[i][:-4]}.png"), dpi=300,bbox_inches='tight')
                plt.close(fig)
                
                fig, ax = plt.subplots()
                ax.hist(ndvi[i].flatten(),label="NDVI",color="green",bins=200,range=(-1,1))
                plt.xlabel('NDVI')
                plt.ylabel('Frecuencia')
                plt.grid(True)
                plt.ioff()
                plt.savefig(os.path.join(os.path.join(ruta,f"graficos"),f"histograma_NDVI_{names[i][:-4]}.png"), dpi=300,bbox_inches='tight')
                plt.close(fig)
            
            print("Graficos guardados :D")
               
        def alertas(x,ruta,crs,transform):
            os.mkdir(os.path.join(ruta,"deteccion"))
            matriz = np.empty((len(x[-1]),len(x[-1][0])))
            matriz[:] = np.nan
            c=0
            tip={0:"densa",1:"moderada",2:"escasa",3:"limpio"}
            ar=open(os.path.join(os.path.join(ruta,"deteccion"),"registro.txt"),"w")
            for i in range(len(x[-1])):
                for e in range(len(x[-1][i])):
                    if not(np.isnan(x[-1][i][e])) and not(np.isnan(x[-2][i][e])):
                    #print(tip[clas(x[-1][i][e])],tip[clas(x[-2][i][e])])
                        if tip[clas(x[-1][i][e])]!=tip[clas(x[-2][i][e])]:
                            ar.write(f"{tip[clas(x[-1][i][e])]} - {tip[clas(x[-2][i][e])]} | {x[-1][i][e]} - {x[-2][i][e]}\n")
                            matriz[i][e]=cambio2(clas(x[-2][i][e]),clas(x[-1][i][e]))
                        c+=1
            ar.close()
            matriz=matriz.astype("float32")
            geometry = [shape(geom) for geom, value in rasterio.features.shapes(matriz, transform=transform) if not(np.isnan(value))]
            gdf = gpd.GeoDataFrame({'geometry': geometry},crs=crs)
            gdf['valor'] = [value for geom, value in rasterio.features.shapes(matriz, transform=transform) if not(np.isnan(value))]
            gdf['area'] = gdf['geometry'].area
            gdf['cambio']= [f"{tip[np.where(factor==int(value))[0][0]]} >> {tip[np.where(factor==int(value))[1][0]]}" for geom, value in rasterio.features.shapes(matriz, transform=transform) if not(np.isnan(value))]
            gdf['dscrpcn']=[f"Posible INCREMENTO de vegetacion" if int(value) in (4,7,8,10,11,12) else f"Posible DISMINUCION de vegetacion" for geom, value in rasterio.features.shapes(matriz, transform=transform) if not(np.isnan(value))]
            gdf = gdf[gdf['geometry'].area >= 37]
            gdf_menos=gdf[gdf['valor'].isin([1,2,3,5,6,9])]
            gdf_mas=gdf[gdf['valor'].isin([4,7,8,10,11,12])]
            gdf.to_file(os.path.join(os.path.join(ruta,"deteccion"),"alertas.shp"))
            gdf_menos.to_file(os.path.join(os.path.join(ruta,"deteccion"),"posible_perdida.shp"))
            gdf_mas.to_file(os.path.join(os.path.join(ruta,"deteccion"),"posible_incremento.shp"))
            print(f'Archivo shapefile creado en: {os.path.join(ruta,"deteccion")}')
            #shp=gpd.read_file(os.path.join(os.path.join(ruta,"deteccion"),"alerta.shp"))                                                       
            #gpd.io.file.fiona.drvsupport.supported_drivers['KML']='rw'  
            #shp.to_file("prueba2.kml",driver="KML")  
        #--------------------------------------------------
        
        inicio=datetime.now()
        if tipo==1:
            tifs=listar_tif(self.directorio)
            imgs=[rs.open(os.path.join(ruta,i)) for i in tifs]
            arrays=[i.read().astype('float64') for i in imgs]
            ndvis=[ndvi(i[2],i[3]) for i in arrays]
            ruta_resultado=crear_carpeta(self.ruta)
            guardar_ndvi(ruta_resultado,tifs,ndvis,imgs[0].crs,imgs[0].width,imgs[0].height,imgs[0].transform)
            mostrar_ndvi_individual(ruta_resultado,tifs,ndvis,1)
            alertas(ndvis,ruta_resultado,imgs[0].crs,imgs[0].transform)
            ventana=ventana_secundaria()
            ventana.generado_correctamente_unico(ruta)
        else:
            carpetas=self.directorio
            if "resultado" in self.directorio:
                carpetas=self.directorio[:self.directorio.index("resultado")]
                print(self.directorio)
            ruta_resultado=crear_carpeta(self.ruta)
            pro=1/len(self.directorio)
            for i in carpetas:
                print(f"\nTrabajando en {i}")
                ruta_c=os.path.join(ruta,i)
                tifs=listar_tif(os.listdir(ruta_c))
                imgs=[rs.open(os.path.join(ruta_c,i)) for i in tifs]
                arrays=[i.read().astype('float64') for i in imgs]
                ndvis=[ndvi(i[2],i[3]) for i in arrays]
                os.mkdir(os.path.join(ruta_resultado,i))
                guardar_ndvi(os.path.join(ruta_resultado,i),tifs,ndvis,imgs[0].crs,imgs[0].width,imgs[0].height,imgs[0].transform)
                mostrar_ndvi_individual(os.path.join(ruta_resultado,i),tifs,ndvis,0) 
                print("_______________________________________________") 
            ventana=ventana_secundaria()
            ventana.generado_correctamente_unico(ruta)
            print(self.directorio)
        print(f"tiempo total: {(datetime.now()-inicio).total_seconds()} segundos | {(datetime.now()-inicio).total_seconds()*1000} milisegundos")
        """
        #--------------------------------------------------
        #lectura de imagenes

        img1=rs.open("./img/punto_1/planet2020.tif")
        img2=rs.open("./img/punto_1/img_sentinel2_2021.tif")

        #--------------------------------------------------
        #sentinel red=0 green=1 blue=2 nir=3
        #planet psscene blue=0 green=1 red=2 nir=3
        #extracción de bandas 
        array_img1=img1.read().astype('float64')
        img1_red=array_img1[2]
        img1_nir=array_img1[3]
        ndvi_img1=ndvi(img1_red,img1_nir)

        array_img2=img2.read().astype('float64')
        img2_red=array_img2[0]
        img2_nir=array_img2[3]
        ndvi_img2=ndvi(img2_red,img2_nir)


        #-------------------------------------------------- gist_earth gray viridis
        #mostrar imagenes bases
        fig,((ax1, ax2), (ax3, ax4))=plt.subplots(2,2)

        ax1.imshow(verdadero_color(array_img1[2],array_img1[1],array_img1[0]))
        ax1.axis("off")
        ax1.set_title("2020",fontdict={'weight':'bold'})

        ax2.imshow(verdadero_color(array_img2[0],array_img2[1],array_img2[2]))
        ax2.axis("off")
        ax2.set_title("2021",fontdict={'weight':'bold'})


        #mostrar ndvi
        plot.show(ndvi_img1,ax=ax3,cmap="RdYlGn",title="NDVI 2020")
        ax3.axis("off")
        plot.show(ndvi_img2,ax=ax4,cmap="RdYlGn",title="NDVI 2021")
        ax4.axis("off")

        plt.suptitle("Prueba piloto 01",weight='bold',size=16)
        plt.show()

        #---------------------------------------------------
        #histograma ndvi

        fig,((ax1, ax2), (ax3, ax4))=plt.subplots(2,2)
        plot.show(ndvi_img1,ax=ax1,cmap="RdYlGn",title="NDVI 2020")
        ax2.hist(ndvi_img1.flatten(),label="NDVI",color="green",bins=200)

        plot.show(ndvi_img2,ax=ax3,cmap="RdYlGn",title="NDVI 2021")
        ax4.hist(ndvi_img2.flatten(),label="NDVI",color="green",bins=200)

        plt.suptitle("Prueba piloto 01",weight='bold',size=16)
        plt.show()
        #---------------------------------------------------
        #ndvi individuales
        plt.figure(figsize=(10, 10))
        plt.imshow(ndvi_img1, cmap='RdYlGn',vmax=1)
        plt.colorbar(label='NDVI')
        plt.suptitle('Índice de Vegetación de Diferencia Normalizada (NDVI) para 2020',weight='bold',size=16)
        plt.axis('off')
        info(ndvi_img1)
        plt.subplots_adjust(right=0.83)
        plt.show()

        plt.figure(figsize=(10, 10))
        plt.imshow(ndvi_img2, cmap='RdYlGn',vmax=1)
        plt.colorbar(label='NDVI')
        plt.suptitle('Índice de Vegetación de Diferencia Normalizada (NDVI) para 2021',weight='bold',size=16)
        plt.axis('off')
        info(ndvi_img2)
        plt.subplots_adjust(right=0.83)
        plt.show()

        #---------------------------------------------------

        plt.figure(figsize=(10, 10))
        plt.imshow(clasificacion(ndvi_img2), cmap='RdYlGn',vmax=1)
        plt.colorbar(label='NDVI')
        plt.suptitle('Clasificación NDVI para 2020',weight='bold',size=16)
        plt.axis('off')
        plt.subplots_adjust(right=0.83)
        plt.show()


        #--------------------------------------------------

"""