#Various functions for calculating some cosmological stuff
import const
import numpy as np
from scipy.integrate import quadrature
from scipy.interpolate import interp1d
from helper_functions import outputify

#Precalculated table of comoving distances at various redshifts
precalc_table_z = 10**np.linspace(0,2,200)
precalc_table_cdist = np.array([  3367.12811226,   3425.76323848,   3484.98198942,   3544.77422924,
         3605.12931532,   3666.03610672,   3727.48297919,   3789.45783628,
         3851.94812421,   3914.94084751,   3978.42258571,   4042.37951119,
         4106.79740797,   4171.66169149,   4236.95742925,   4302.66936216,
         4368.78192668,   4435.2792775 ,   4502.14531073,   4569.36368757,
         4636.91786118,   4704.79108946,   4772.96647586,   4841.42698316,
         4910.15546037,   4979.13466689,   5048.34729652,   5117.77600111,
         5187.4034139 ,   5257.21217235,   5327.18494051,   5397.30443082,
         5467.55342517,   5537.91479547,   5608.37152327,   5678.90672746,
         5749.50364896,   5820.14571617,   5890.81653062,   5961.49988992,
         6032.17980244,   6102.84050111,   6173.46645625,   6244.04238757,
         6314.55327524,   6384.98437005,   6455.32120274,   6525.54960861,
         6595.65567269,   6665.62582636,   6735.44679581,   6805.10562103,
         6874.58966023,   6943.88659351,   7012.98442588,   7081.8714896 ,
         7150.53644589,   7218.96828601,   7287.15635902,   7355.09026615,
         7422.760013  ,   7490.15591046,   7557.26859681,   7624.08903586,
         7690.6085146 ,   7756.81864061,   7822.711339  ,   7888.27884918,
         7953.51376147,   8018.40885522,   8082.95732541,   8147.15262911,
         8210.98851714,   8274.45902935,   8337.55848979,   8400.28150177,
         8462.62299146,   8524.57801124,   8586.14201412,   8647.31066739,
         8708.07989107,   8768.44585245,   8828.40496057,   8887.95386081,
         8947.0894879 ,   9005.80882742,   9064.1092537 ,   9121.98830059,
         9179.44371043,   9236.47342869,   9293.07559857,   9349.24865046,
         9404.99092404,   9460.30116256,   9515.1783261 ,   9569.62142812,
         9623.62968515,   9677.20257775,   9730.33944157,   9783.04000267,
         9835.30418168,   9887.13190876,   9938.52329263,   9989.47868761,
        10039.9982429 ,  10090.082495  ,  10139.73216028,  10188.94791529,
        10237.73059636,  10286.08127025,  10334.00073733,  10381.49018974,
        10428.55099169,  10475.18441427,  10521.39200307,  10567.17500485,
        10612.53505099,  10657.47393231,  10701.99331917,  10746.09514682,
        10789.78095337,  10833.05292603,  10875.91300168,  10918.36323508,
        10960.40590215,  11002.04272373,  11043.27628018,  11084.10873513,
        11124.54256296,  11164.57966547,  11204.22280202,  11243.47430133,
        11282.33679709,  11320.81233011,  11358.90380788,  11396.61368616,
        11433.94472308,  11470.89906158,  11507.47972977,  11543.68927684,
        11579.53043981,  11615.00577464,  11650.11806327,  11684.87003285,
        11719.26447527,  11753.304019  ,  11786.99149311,  11820.32972719,
        11853.3213714 ,  11885.96928129,  11918.27625131,  11950.2451204 ,
        11981.87858385,  12013.17950408,  12044.15072832,  12074.79495382,
        12105.11504387,  12135.11384232,  12164.79404351,  12194.15850168,
        12223.21004701,  12251.95136655,  12280.38529678,  12308.51464473,
        12336.34208696,  12363.87043424,  12391.1024615 ,  12418.04083312,
        12444.68832668,  12471.04767629,  12497.12153436,  12522.91266416,
        12548.42367179,  12573.65727854,  12598.61615879,  12623.30290476,
        12647.72021033,  12671.87062361,  12695.75679425,  12719.38131816,
        12742.74673137,  12765.85563654,  12788.7105263 ,  12811.31398206,
        12833.6684563 ,  12855.77648483,  12877.64054123,  12899.26307071,
        12920.6465364 ,  12941.7933441 ,  12962.70592637,  12983.38665203,
        13003.83791968,  13024.06206321,  13044.06144437,  13063.83836398,
        13083.39514428,  13102.73405492,  13121.8573761 ,  13140.76734823])

def _ldist(z):
    # This function is used for the integration in luminosity_distance  
    # Only meant for internal use.
    term1 = (1+z)**2
    term2 =  1.+2.*(const.q0+const.lam)*z
    term3 = z*(2.+z)*const.lam
    denom = (term1*term2 - term3)
    if type(z) is np.ndarray:
        out = np.zeros(z.shape)
        good = np.where(denom > 0.0)[0]
        out[good] = 1.0/np.sqrt(denom[good])
        return out
    else:
        if denom >= 0:
            return 1.0/np.sqrt(denom)
        else:
            return 0.0


def luminosity_distance(z, k=0):
    ''' Calculate the luminosity distance for a given redshift.
    
    Parameters:
        * z (float or array): the redshift(s)
        * k = 0 (float): the curvature constant.
        
    Returns:
        The luminosity distance in Mpc
     '''

    if not (type(z) is np.ndarray): #Allow for passing a single z
        z = np.array([z])
    n = len(z)

    if const.lam == 0:
        denom = np.sqrt(1+2*const.q0*z) + 1 + const.q0*z 
        dlum = (const.c*z/const.H0)*(1 + z*(1-const.q0)/denom)
        return dlum
    else:
        dlum = np.zeros(n)
        for i in xrange(n):
            if z[i] <= 0:
                dlum[i] = 0.0
            else:
                dlum[i] = quadrature(_ldist, 0, z[i])[0]

    if k > 0:
        dlum = np.sinh(np.sqrt(k)*dlum)/np.sqrt(k)
    elif k < 0:
        dlum = np.sin(np.sqrt(-k)*dlum)/np.sqrt(-k)
    return outputify(const.c*(1+z)*dlum/const.H0)


def z_to_cdist(z):
    ''' Calculate the comoving distance 

    Parameters:
        z (float): redshift

    Returns:
        Comoving distance in Mpc
    '''
    Ez_func = lambda x: 1./np.sqrt(const.Omega0*(1.+x)**3+const.lam)
    dist = const.c/const.H0 * quadrature(Ez_func, 0, z)[0]
    return outputify(dist)


def cdist_to_z(dist):
    ''' Calculate the redshift correspoding to the given redshift. 

    Parameters:
        * dist (float): the distance in comoving Mpc

    Returns:
        redshift corresponding to the distance.

        .. note::
            Uses a precalculated table for interpolation. Only valid for 
            0 < z < 100 
        
    '''

    func = interp1d(precalc_table_cdist, precalc_table_z, kind='cubic')
    z = func(dist)
    return z


def angular_size(dl, z):
    ''' Calculate the angular size of an object at a given
    redshift.
    
    Parameters:
        * dl (float or array): the physical size in kpc
        * z (float or array): the redshift of the object
        
    Returns:
        The angluar size in arcseconds 
        
    '''

    angle = 180./(3.1415)*3600.*dl*(1+z)**2/(1000*luminosity_distance(z))
    return outputify(angle)


def nu_to_z(nu21):
    ''' Convert 21 cm frequency in MHz to redshift 

    Parameters:
        * nu21 (float or array): redshifted 21 cm frequency in MHz

    Returns:
        Redshift
        
    '''
    return const.nu0/nu21-1

def z_to_nu(z):
    ''' Get the 21 cm frequency that corresponds to redshift z 

    Parameters:
        * z (float or array): redshift

    Returns:
        redshifted 21 cm frequency in MHz
        
    '''
    return const.nu0/(1.+z)

def nu_to_cdist(nu21):
    ''' Calculate the comoving distance to a given 21 cm frequency 

    Parameters:
        * nu21 (float or array): redshifted 21 cm frequency in MHz

    Returns:
        Comoving distance in Mpc
    
    '''
    redsh = nu_to_z(nu21)
    return z_to_cdist(redsh)
    
def c_to_p(z_to_cdist, z):
    '''
    Convert comoving distance to proper distance
    
    Parameters:
        * z_to_cdist: The comoving distance
        * z: the redshift
        
    Returns:
        Proper distance
    '''
    return z_to_cdist/(1+z)


def p_to_c(pdist, z):
    '''
    Convert proper distance to comoving distance
    
    Parameters:
        * pdist: The proper distance
        * z: the redshift
        
    Returns:
        Comoving distance
    '''
    
    return pdist*(1+z)

