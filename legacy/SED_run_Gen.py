def SED_fit(phot_filename):
    import pandas as pd
    import timeit
    import numpy as np
    import copy
    import matplotlib.pyplot as plt
    import os
    import csv
    import matplotlib.backends.backend_pdf
    import astropy
    from astropy import units as u
    from astropy.coordinates import SkyCoord
    from astropy.table import Table
    from scipy import interpolate
    from scipy.interpolate import interp1d 
    from astropy.io import ascii
    dict_of_wavelength_info={'Gmag': [23, 5836.3, 2835.1, 0.93444], 'BPmag': [27, 5020.9, 3393.3, 1.12978], 'RPmag': [31, 7588.8, 2485.1, 0.66304], 'gpsmag': [18, 4775.6, 3909.1, 1.2013], 'rpsmag': [23, 6129.5, 3151.4, 0.88592], 'ipsmag': [28, 7484.6, 2584.6, 0.67699], 'zpsmag': [33, 8657.8, 2273.1, 0.51994], 'ypsmag': [38, 9613.5, 2203.0, 0.44049], 'Jmag': [20, 12350, 1594, 0.28726], 'Hmag': [23, 16620, 1024, 0.17256], 'Ksmag': [26, 21590, 666.7, 0.11157], 'IRAC1mag': [74, 35075.1, 280.9, 0.04913], 'IRAC2mag': [76, 44365.8, 179.7, 0.03504], 'IRAC3mag': [78, 56281.0, 115.0, 0.0265], 'IRAC4mag': [80, 75891.6, 64.9, 0.0265], 'W1mag': [0, 33526.0, 309.5, 0.05296], 'W2mag': [0, 46028.0, 171.8, 0.03252], 'W3mag': [0, 115608.0, 31.7, 0.0265], 'W4mag': [0, 220883.0, 8.4, 0.0265], 'JsBmag': [0, 4378.1, 4023.8, 1.31758], 'JsVmag': [0, 5466.1, 3562.5, 0.99997], 'JsRmag': [0, 6695.6, 2814.9, 0.79224], 'JsImag': [0, 8565.1, 2282.8, 0.53235], 'Rcmag': [0, 6358.0, 3028.0, 0.84811], 'Icmag': [0, 7829.2, 2458.3, 0.63086], 'umag': [0, 3594.9, 1568.5, 1.55723], 'gmag': [0, 4640.4, 3965.9, 1.24072], 'rmag': [0, 6122.3, 3162.0, 0.88711], 'imag': [0, 7439.5, 2602.0, 0.68303], 'zmag': [0, 8897.7, 2244.7, 0.48782], 'upmag': [0, 3542.2, 1469.5, 1.57151], 'gpmag': [0, 4724.6, 3921.0, 1.21617], 'rpmag': [0, 6202.6, 3112.9, 0.87382], 'ipmag': [0, 7673.0, 2502.6, 0.65177], 'zpmag': [0, 10506.5, 1821.0, 0.39009], 'gxfuvmag': [0, 1549.0, 520.7, 2.60956],'JsUmag': [0, 3570.6, 1564.2, 1.4258], 'gxnuvmag': [0, 2304.7, 788.5, 2.79148], 'VistaJmag': [0, 12481.0, 1550.7, 0.28276], 'VistaHmag': [0, 16348.2, 1027.3, 0.17979], 'VistaKmag': [0, 21435.5, 669.6, 0.11460],'N_Ksmag': [0, 21240.60, 677.43, 0.1170],'Lpmag': [0, 37301.72, 248.30, 0.04621],'IPHAS_Hamag':[0,6568.2,2609.8,0.81]}
    '''
    dict_of_wavelength_info={'Gmag': [23, 5836.3, 2835.1, 0.948], 'BPmag': [27, 5020.9, 3393.3, 1.08017], 'RPmag': [31, 7588.8, 2485.1, 0.71945], 'gpsmag': [18, 4775.6, 3909.1, 1.12435], 'rpsmag': [23, 6129.5, 3151.4, 0.908], 'ipsmag': [28, 7484.6, 2584.6, 0.7318], 'zpsmag': [33, 8657.8, 2273.1, 0.59272], 'ypsmag': [38, 9603.1, 2206.0, 0.51298], 'Jmag': [20, 12350, 1594, 0.33454], 'Hmag': [23, 16620, 1024, 0.20096], 'Ksmag': [26, 21590, 666.7, 0.12993], 'IRAC1mag': [74, 35075.1, 280.9, 0.05721], 'IRAC2mag': [76, 44365.8, 179.7, 0.04081], 'IRAC3mag': [78, 56281.0, 115.0, 0.03086], 'IRAC4mag': [80, 75891.6, 64.9, 0.03086], 'W1mag': [0, 33526.0, 309.5, 0.06168], 'W2mag': [0, 46028.0, 171.8, 0.03787], 'W3mag': [0, 115608.0, 31.7, 0.03086], 'W4mag': [0, 220883.0, 8.4, 0.03086], 'JsBmag': [0, 4378.1, 4023.8, 1.1958],'JsUmag': [0, 3570.6, 1564.2, 1.2858], 'JsVmag': [0, 5466.1, 3562.5, 0.99998], 'JsRmag': [0, 6695.6, 2814.9, 0.83078], 'JsImag': [0, 8565.1, 2282.8, 0.60371], 'Rcmag': [0, 6358.0, 3028.0, 0.87683], 'Icmag': [0, 7829.2, 2458.3, 0.69095], 'umag': [0, 3594.9, 1568.5, 1.32448], 'gmag': [0, 4640.4, 3965.9, 1.1487], 'rmag': [0, 6122.3, 3162.0, 0.90899], 'imag': [0, 7439.5, 2602.0, 0.73715], 'zmag': [0, 8897.7, 2244.7, 0.56428], 'upmag': [0, 3542.2, 1469.5, 1.32692], 'gpmag': [0, 4724.6, 3921.0, 1.13354], 'rpmag': [0, 6202.6, 3112.9, 0.89803], 'ipmag': [0, 7673.0, 2502.6, 0.70947], 'zpmag': [0, 10506.5, 1821.0, 0.45429], 'gxnuvmag': [0, 1549.0, 520.7, 1.48909], 'gxfuvmag': [0, 2304.7, 788.5, 1.79283]}

    '''


    Vega_mag_optbands=['Gmag','BPmag','RPmag','Icmag','Rcmag','JsVmag','JsBmag','JsUmag','JsRmag','JsImag','Jmag','Hmag','Ksmag','IRAC1mag','IRAC2mag','IRAC3mag','IRAC4mag','W1mag','W2mag','W3mag','W4mag','VistaJmag','VistaHmag','VistaKmag','N_Ksmag','Lpmag','IPHAS_Hamag']
    AB_mag_optbands=['gpsmag', 'rpsmag', 'ipsmag', 'zpsmag', 'ypsmag','gpmag','rpmag','ipmag','gxnuvmag','gxfuvmag','umag','gmag','rmag','imag','zmag']#should add more optical bands respectively
    wv_info=copy.deepcopy(dict_of_wavelength_info)
    list_all_wavelengths_mstr=[p[1] for p in list(wv_info.values())] 
    zero_magnitude_flux_mstr=[p[2] for p in list(wv_info.values())]
    objct_flux_data=dict() 
    all_obj_wavelengths=dict()                          # Dictionary containing all the wavelength bands (wavelength values) that are available for the stars showing IR excess.
    all_objct_flux_data_list=dict()
    all_obj_extinction = dict()
    
    star_phot_data = pd.read_csv(phot_filename,na_values=['-','999','-999'])

    for index,row in star_phot_data.iterrows():
        AV = np.float(row['Av'])
        Star_name = row['Name']
        Distance_pc = np.float(row['Dist'])
    #print(index)    
    opt_bands=[]
    bands=[]
    lis_opt_wvls=[]## Only if the object has data in all 2MASS bands plus IRAC 1&2, is the object considered for furter analysis
        #print(row[['Jmag','Hmag','Ksmag','IRAC1mag','IRAC2mag']].notna())
    obj_bands=[]################################
    list_all_wavelengths=[]
    dict_obj_mags = dict()
    flux_wvlngth=dict()
    flx_err=dict()
    err_cnt=0
    dict_obj_mags_wo_corctn = dict()
    dict_obj_mags_err = dict()
    for bnd_nm in dict_of_wavelength_info:
        all_obj_extinction[bnd_nm] = dict_of_wavelength_info[bnd_nm][3]*AV
    for bnd_nm in dict_of_wavelength_info:
                if (bnd_nm in star_phot_data.columns) and (row[[bnd_nm]].notna().sum()) == 1:
                    opt_bands.append(bnd_nm)
                    dict_obj_mags[bnd_nm]=float(row[bnd_nm])-all_obj_extinction[bnd_nm]
                    dict_obj_mags_wo_corctn[bnd_nm]=float(row[bnd_nm])
                    dict_obj_mags_err[bnd_nm]=float(row['e_'+bnd_nm])
                    lis_opt_wvls.append(wv_info[bnd_nm][1])
    bands=opt_bands+bands
    list_all_wavelengths=lis_opt_wvls+list_all_wavelengths
    list_opt_flx=[]
    list_opt_flx_err=[]
    for bnd_nm in opt_bands:
        if bnd_nm in Vega_mag_optbands:
            #print('sdfgds')
            mag_wvlngth=dict_obj_mags[bnd_nm]
            flux_wvlngth[bnd_nm]=(2.99792458e-05*(wv_info[bnd_nm][2]*10**(-mag_wvlngth/2.5)))/(wv_info[bnd_nm][1]**2)# Converting magnitude to flux in Jansky -> Converting Janksy to erg/cm2/s/A (formula from "http://www.stsci.edu/~strolger/docs/UNITS.txt") -> Finally multiplying with wvelength to get lambda*F_lambda in erg/cm2/s.
            list_opt_flx.append(flux_wvlngth[bnd_nm])
            mg_err=mag_wvlngth+float(row['e_'+bnd_nm])
            if float(row['e_'+bnd_nm])>90:
                mg_err=mag_wvlngth
            err_corctd_flx=(2.99792458e-05*(wv_info[bnd_nm][2]*10**(-mg_err/2.5)))/(wv_info[bnd_nm][1]**2)
            flx_err[bnd_nm]=flux_wvlngth[bnd_nm]-err_corctd_flx
            list_opt_flx_err.append(flx_err[bnd_nm])
        if bnd_nm in AB_mag_optbands:
            mag_wvlngth=dict_obj_mags[bnd_nm]
            flux_wvlngth[bnd_nm]=(2.99792458e-05*(3631*10**(-mag_wvlngth/2.5)))/(wv_info[bnd_nm][1]**2)           # Converting magnitude to flux in Jansky -> Converting Janksy to erg/cm2/s/A (formula from "http://www.stsci.edu/~strolger/docs/UNITS.txt") -> Finally multiplying with wvelength to get lambda*F_lambda in erg/cm2/s.
            list_opt_flx.append(flux_wvlngth[bnd_nm])
            mg_err=mag_wvlngth+float(row['e_'+bnd_nm])
            if float(row['e_'+bnd_nm])>90:
                mg_err=mag_wvlngth
            err_corctd_flx=(2.99792458e-05*(3631*10**(-mg_err/2.5)))/(wv_info[bnd_nm][1]**2)
            flx_err[bnd_nm]=flux_wvlngth[bnd_nm]-err_corctd_flx
            list_opt_flx_err.append(flx_err[bnd_nm])
                                                    
        objct_flux_data[index]=flux_wvlngth
        obj_nor_band_flux=objct_flux_data[index][opt_bands[0]]
    #print(flux_wvlngth,flx_err)
    a=[]
    b=[]
    for bnd_nm in bands:
        a.append(flux_wvlngth[bnd_nm])
        b.append(dict_of_wavelength_info[bnd_nm][1])
    final_dic = dict()
    final_dic1 = dict()
    final_dic2 = dict()
    for bnd_nm in flux_wvlngth:
        final_dic[bnd_nm]=flux_wvlngth[bnd_nm]
        final_dic1[bnd_nm] = dict_of_wavelength_info[bnd_nm][1]
        final_dic2[bnd_nm] = flx_err[bnd_nm]

    from itertools import chain
    from collections import defaultdict
    FINAL_DIC = defaultdict(list)
    for d in (final_dic1, final_dic, final_dic2): # you can list as many input dicts as you want here
        for key, value in d.items():
            FINAL_DIC[key].append(value)
    FINAL_DIC = dict(sorted(FINAL_DIC.items(), key=lambda k_v: k_v[1][0]))
    
    x = []
    y = []
    z = []
    for i in FINAL_DIC:
        #print(A[i][0])
        #a = A[i][1]
        x.append(FINAL_DIC[i][0])
        y.append(FINAL_DIC[i][1])
        z.append(FINAL_DIC[i][2])
    sed_fitting_bands=['BPmag','Gmag','RPmag']
    filename_count = 0
    Temp_filename_dict = dict()
    least_sq_theo_sed=dict()

    path_to_theo_phot = "/home/arun/Desktop/PAH_V2/SED/bt-nextgen-agss2009_phot_1587193332.0893"
    for filename in os.listdir(path_to_theo_phot):
        filename_count+=1 
        indv_wvl_lambda_Flambda=dict()
        Temp_filename_dict[filename_count]=filename
        data = ascii.read(path_to_theo_phot+"/"+filename)
        A_wave = data.columns[1]
        B_flux = data.columns[2]
        Band_norm = 'Gmag'
        wavel_n1 = FINAL_DIC[Band_norm][0]
        flux_n1 = FINAL_DIC[Band_norm][1]
        index_fit = near(A_wave,wavel_n1)
        norm_phot_flux = (B_flux/B_flux[index_fit])*flux_n1
        least_sq = []
        for chi_bnd in sed_fitting_bands:
            index_fit = near(A_wave,FINAL_DIC[chi_bnd][0])
            nor_temp_band_lambda_Flambda = norm_phot_flux[index_fit]
            obj_lambda_Flambda=FINAL_DIC[chi_bnd][1]# Object lambda_Flambda at that wavelength.
            obj_flx_err=FINAL_DIC[chi_bnd][2]# observed flux error in that band
            if obj_flx_err==0: # If there is not error then a high error value of 1 is taken.
                obj_flx_err=1
            x2=((obj_lambda_Flambda-nor_temp_band_lambda_Flambda)**2/nor_temp_band_lambda_Flambda)                                                         # Chi-squared or least sqaured formula using the theoretical and observed lambda_Flambda.
            least_sq.append(x2)
            total_x2=(1/(len(sed_fitting_bands)-1))*sum(least_sq)
        least_sq_theo_sed[filename]=sum(least_sq)
    spec_phot_filename=min(least_sq_theo_sed, key=least_sq_theo_sed.get)
    #print(spec_phot_filename)
    eff_temp=float(spec_phot_filename[23:26])*100# The effective temperature of the best fit spectra
    sur_g=float(spec_phot_filename[27:30])
    #print(eff_temp,sur_g)

    path_to_theo_spectra = "/home/arun/Desktop/PAH_V2/SED/bt-nextgen-agss2009"

    for spec_filename in os.listdir(path_to_theo_spectra):
        if spec_filename[3:6] == spec_phot_filename[23:26] and spec_filename[7:10] == spec_phot_filename[27:30]:
            spectra_fit_filename=spec_filename
    data_spectra_fit_filename = ascii.read(path_to_theo_spectra+"/"+spectra_fit_filename)
#print(spectra_fit_filename)
    data_PHOT = ascii.read(path_to_theo_phot+"/"+spec_phot_filename)

    Spec_wave = data_spectra_fit_filename.columns[0]
    Spec_flux = data_spectra_fit_filename.columns[1]
    Spec_index_fit = near(Spec_wave,wavel_n1)
    norm_spec_flux = (Spec_flux/Spec_flux[Spec_index_fit])*flux_n1
    A_wave = data_PHOT.columns[1]
    B_flux = data_PHOT.columns[2]
    index_fit = near(A_wave,wavel_n1)
    Md = flux_n1/B_flux[index_fit]
    norm_phot_flux = (B_flux*Md)
    Radius = np.sqrt(Md*Distance_pc**2)*4.435e+7
    print("Star_name = ",Star_name,"Teff = ",eff_temp,"log g = ",sur_g,"Radius = ",Radius)
    result = [Star_name,eff_temp,sur_g,Radius]
    wvx = []
    wvy = []
    for ss in FINAL_DIC:
        ind = near(A_wave,FINAL_DIC[ss][0])
        wvx.append(A_wave[ind])
        wvy.append(norm_phot_flux[ind])
    plt.errorbar(x,y,yerr=z,marker='o',ms=10, mfc='red',ls='none',label='%s'%Star_name)
    plt.scatter(wvx,wvy,color='b',s=40,label='Model_photometry')
    plt.plot(Spec_wave,norm_spec_flux,'k-',linewidth=1,alpha=0.4,label='BT-NextGen(AGSS2009)\nTeff = %s K, log g = %s'%(str(eff_temp)[:-2],sur_g))
    plt.legend(loc='best',prop={'size': 10,'weight':'bold'}, ncol=1)
    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel('Wavelength ($\AA$)',fontsize=18,fontweight='bold')
    plt.ylabel('$F_\lambda$ $(erg/cm^2 /s/\AA)$',fontsize=18,fontweight='bold')
    plt.xlim(min(x)-500,max(x)+5000)
    plt.ylim(min(y)-(min(y)/0.21e1),max(y)+(max(y)/0.21e1))
    fig =plt.gcf()
    fig.set_size_inches(13.5, 8.5)
    fig.savefig("/home/arun/Desktop/SED/General_SED/SED_Images/SED_%s.png"%Star_name)
    fig.clear()
    with open("/home/arun/Desktop/SED/LAMOST_Analysis/Anusha_Be_res.csv", 'a') as writeFile1:
        writer = csv.writer(writeFile1)
        np.savetxt(writeFile1,[result], delimiter=',', fmt='%s')
        writeFile1.close()
    return(FINAL_DIC,Star_name)


def near(A,value):
    import numpy as np
    idx = (np.abs(A-value)).argmin()
    return (idx)

def sed_file_gen(Name, Av):
    from astroquery.vizier import Vizier
    from astroquery.mast import Catalogs
    import astropy.units as units
    import matplotlib.pyplot as plt
    import astropy.units as u
    import astropy.coordinates as coord
    import os
    import csv
    import numpy as np
    v = Vizier(columns=["*", "+_r"])
    Phot_Name = []
    Gaia_dat = ['Name','RA','DEC','Av','Dist','Gmag','e_Gmag','BPmag','e_BPmag','RPmag','e_RPmag']
    TWOMASS_dat = ['Jmag','e_Jmag','Hmag','e_Hmag','Ksmag','e_Ksmag']
    WISE_dat = ['W1mag','e_W1mag','W2mag','e_W2mag','W3mag','e_W3mag','W4mag','e_W4mag']
    SDSS_dat = ['umag','e_umag','gmag','e_gmag','rmag','e_rmag','imag','e_imag','zmag','e_zmag']
    B_V_dat = ['JsBmag','e_JsBmag','JsVmag','e_JsVmag']
    Phot = []
    try:#
        Gaia = v.query_region(Name, radius="5s",catalog="I/345/gaia2")
        Star_ID = Gaia[0][0]['Source']
        Bailer = v.query_region('Gaia DR2 '+str(Star_ID), radius="2s",catalog="I/347/gaia2dis")
        print(len(Gaia[0]))
        Phot_Name.append(Gaia_dat)
        Phot_Name = np.reshape(Phot_Name, (11))
        A = [Name,Gaia[0][0]['RA_ICRS'],Gaia[0][0]['DE_ICRS'],Av,Bailer[0][0]['rest'],Gaia[0][0]['Gmag'],
             Gaia[0][0]['e_Gmag'],Gaia[0][0]['BPmag'],Gaia[0][0]['e_BPmag'],Gaia[0][0]['RPmag'],
             Gaia[0][0]['e_RPmag']]
        Phot.append(A)
        A = np.reshape(A, (11))
    except:
        IndexError
    try:#
        twomass = v.query_region(Name, radius="5s",catalog="II/246/out")
        print(len(twomass[0]))
        Phot_Name = np.append(Phot_Name,TWOMASS_dat)
        B = [twomass[0][0]["Jmag"],twomass[0][0]["e_Jmag"],twomass[0][0]["Hmag"],
             twomass[0][0]["e_Hmag"],twomass[0][0]["Kmag"],twomass[0][0]["e_Kmag"],]
        Phot = np.append(Phot,B)
    
    except:
        IndexError
    try:#
        wise = v.query_region(Name, radius="5s",catalog="II/328/allwise")
        print(len(wise[0]))
        Phot_Name = np.append(Phot_Name,WISE_dat)
        C = [wise[0][0]['W1mag'],wise[0][0]['e_W1mag'],wise[0][0]['W2mag'],wise[0][0]['e_W2mag'],
             wise[0][0]['W3mag'],wise[0][0]['e_W3mag'],wise[0][0]['W4mag'],wise[0][0]['e_W4mag']]
        Phot = np.append(Phot,C)
    except:
        IndexError

    
    try:#
        sdss = v.query_region(Name, radius="5s",catalog="V/147/sdss12")
        print(len(sdss[0]))
        Phot_Name = np.append(Phot_Name,SDSS_dat)
        D = [sdss[0][0]['umag'],sdss[0][0]['e_umag'],sdss[0][0]['gmag'],sdss[0][0]['e_gmag'],
             sdss[0][0]['rmag'],sdss[0][0]['e_rmag'],sdss[0][0]['imag'],sdss[0][0]['e_imag'],
             sdss[0][0]['zmag'],sdss[0][0]['e_zmag']]
        Phot = np.append(Phot,D)
    except:
        IndexError
    try:
        UCAC = v.query_region(Name, radius="5s", catalog='I/322A/out')
        print(len(UCAC[0]))
        Phot_Name = np.append(Phot_Name,B_V_dat)
        E = [UCAC[0][0]['Bmag'],0.1,UCAC[0][0]['Vmag'],0.1]
        Phot = np.append(Phot,E)    
    except:
        IndexError
    file_name = "/home/arun/Desktop/SED/General_SED/SED_file/SED_%s.csv"%Name
    with open(file_name, 'a') as writeFile1:
        writer = csv.writer(writeFile1)
        np.savetxt(writeFile1,[Phot_Name], delimiter=',', fmt='%s')
        np.savetxt(writeFile1,[Phot], delimiter=',', fmt='%s')
        writeFile1.close()
    return(file_name)

