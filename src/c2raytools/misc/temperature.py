from .. import files
import numpy as np
from .. import const
from .. import utils

def calc_dt(xfrac, dens, z = -1):
	'''
	Calculate the differential brightness temperature assuming T_s >> T_CMB
	
	Parameters:
		* xfrac (XfracFile object, string or numpy array): the ionization fraction
		* dens (DensityFile object, string or numpy array): density in sim units
		* z = -1 (float): The redshift (if < 0 this will be figured out from the files)
		
	Returns:
		The differential brightness temperature as a numpy array with
		the same dimensions as xfrac.
	'''

	#Figure out types of xfrac and dens
	if isinstance(xfrac, files.XfracFile):
		z = xfrac.z
		xi = xfrac.xi.astype('float64')
	elif isinstance(xfrac, str):
		xfile = files.XfracFile(xfrac)
		z = xfile.z
		xi = xfile.xi.astype('float64')
		if z < 0:
			print 'Warning. Please supply a redshift for calc_dt'
	else:
		xi = xi.astype('float64')

	if isinstance(dens, files.DensityFile):
		rho = dens.raw_density.astype('float64')
	elif isinstance(dens, str):
		dfile = files.DensityFile(dens)
		rho = dfile.raw_density.astype('float64')
	else:
		rho = dens.astype('float64')

	utils.print_msg('Calculating differential brightness temperature...')
	utils.print_msg('The redshift is %.3f' % z)

	rho_mean = np.mean(rho)

	#Redshift dependent Hubble constant
	Ez = np.sqrt(const.Omega0*(1.0+z)**3+const.lam+(1.0-const.Omega0-const.lam)*(1.0+z)**2)

	#The temperature box
	Cdt = const.meandt/const.h*(1.0+z)**2/Ez
	dt = Cdt*(1.0-xi)*rho/rho_mean
	
	utils.print_msg('...done')

	return dt
