# -*- coding: utf-8 -*-
"""pyGIMLi - Inversion Frameworks.

These are basic modelling proxies.
"""
import numpy as np

from copy import copy


import pygimli as pg

class Modelling(pg.ModellingBase):
    """Abstract Forward Operator.

    Abstract Forward Operator that use one or more different ModellingBase classes.
    Can be seen as some kind of proxy Forward Operator.

    """
    def __init__(self, **kwargs):

        fop = kwargs.pop('fop', None)
        super(Modelling, self).__init__(**kwargs)
        self._regionProperties = {}
        self._transModel = pg.RTransLog()
        self.fop = None

        self.data = None # dataContainer

        if fop is not None:
            self.setForwardOperator(fop)

    @property
    def transModel(self):
        self._applyRegionProperties()
        if self.regionManager().haveLocalTrans():
            return self.regionManager().transModel()
        return self._transModel

    @transModel.setter
    def transModel(self, tm):
        self._transModel = tm


    def regionManager(self):
        """
        """
        # init RM if necessary
        super(Modelling, self).regionManager()
        # set all local properties
        self._applyRegionProperties()
        return super(Modelling, self).regionManager()

    def setForwardOperator(self, fop):
        self.fop = fop

    def setMesh(self, mesh, ignoreRegionManager=False):

        if self.fop is not None:
            print("Modelling:setMesh", self.fop)
            self.fop.setMesh(mesh, ignoreRegionManager)

            if (not ignoreRegionManager):
                self.setRegionManager(self.fop.regionManagerRef())
        else:
            super(Modelling, self).setMesh(mesh, ignoreRegionManager)

    def clearRegionProperties(self):
        self._regionProperties = {}

    def setRegionProperties(self, region,
                            startModel=None, limits=None, trans=None,
                            cType=None, zWeights=None, modelControl=None):
        """
        """
        if region not in self._regionProperties:
            self._regionProperties[region] = {'startModel': 0,
                                              'modelControl': 1.0,
                                              'zWeights': 1.0,
                                              'cType': 1,
                                              'limits': [0, 0],
                                              'trans': 'Log',
                                              }

        if startModel is not None:
            self._regionProperties[region]['startModel'] = startModel

        if limits is not None:
            self._regionProperties[region]['limits'] = limits

        if trans is not None:
            self._regionProperties[region]['trans'] = trans

        if cType is not None:
            self._regionProperties[region]['cType'] = cType

        if zWeights is not None:
            self._regionProperties[region]['zWeights'] = zWeights

        if modelControl is not None:
            self._regionProperties[region]['modelControl'] = modelControl


    def _applyRegionProperties(self):
        """
        """
        RM = super(Modelling, self).regionManager()

        for rID, vals in self._regionProperties.items():
            RM.region(rID).setStartModel(vals['startModel'])

            RM.region(rID).setModelTransStr_(vals['trans'])

            if 'cType' in vals:
                RM.region(rID).setConstraintType(vals['cType'])

            if 'zWeights' in vals:
                RM.region(rID).setZWeight(vals['zWeights'])

            if 'modelControl' in vals:
                RM.region(rID).setModelControl(vals['modelControl'])

            if vals['limits'][0] > 0:
                RM.region(rID).setLowerBound(vals['limits'][0])

            if vals['limits'][1] > 0:
                RM.region(rID).setUpperBound(vals['limits'][1])

    def createStartModel(self, dataValues, **kwargs):
        """ Create Starting model.

        Create Starting model based on current data values and additional args.
        """
        raise Exception("Implement me in derived classes")

    def setData(self, data):
        #raise Exception("Needed? Implement me in derived classes")
        if self.fop is not None:
            self.fop.setData(data)

    def setDataContainer(self, data):
        if self.fop is not None:
            self.fop.setData(data)
        else:
            super(Modelling, self).setData(data)
            self.data = data

    def setDataBasis(self, **kwargs):
        """Set Data basis, e.g., DataContainer, times, coordinates."""
        data = kwargs.pop('dataContainer', None)
        if isinstance(data, pg.DataContainer):
            self.setDataContainer(data)

    def estimateError(self, data, **kwargs):
        """Create
        """
        raise Exception("Needed?? Implement me in derived classes")
        #data = data * (pg.randn(len(data)) * errPerc / 100. + 1.)
        #return data

    def drawModel(self, ax, model):
        """
        """
        print(ax, model)
        raise Exception("No yet implemented")

    def drawData(self, ax, data, err=None, label=None):
        """
        """
        print(ax, data, err, label)
        raise Exception("No yet implemented")


class Block1DModelling(Modelling):
    """
    """
    def __init__(self, nBlocks=1, **kwargs):
        super(Block1DModelling, self).__init__(**kwargs)
        self._withMultiThread = True
        self._nBlocks = nBlocks

    def setLayers(self, nLayers):
        if nLayers < 2:
            raise Exception("Number of layers need to be at least 2")

        mesh = pg.createMesh1DBlock(nLayers, self._nBlocks)
        self.setMesh(mesh)
        #self.setStartModel(pg.RVector(0))

        for i in range(self._nBlocks + 1):
            self.setRegionProperties(i, trans='log')

        if self._withMultiThread:
            self.setMultiThreadJacobian(2*nLayers - 1)

        self._applyRegionProperties()

    def drawModel(self, ax, model):
        pg.mplviewer.drawModel1D(ax=ax,
                                 model=model,
                                 plot='loglog',
                                 xlabel='Model parameter')
        return ax

    def drawData(self, ax, data, err=None, label=None):
        nData = len(data)
        yVals = range(nData)
        ax.loglog(data, yVals, 'rx-')
        if err is not None:
            ax.errorbar(data, yVals,
                        xerr=err*data,
                        linewidth=1, color='red', linestyle='-')

        ax.set_ylim(max(yVals), min(yVals))
        ax.set_xlabel('Data')
        ax.set_ylabel('Data Number')
        return ax


class MeshModelling(Modelling):
    """
    """
    def __init__(self, **kwargs):
        super(MeshModelling, self).__init__(**kwargs)

    @property
    def paraDomain(self):
        return self.regionManager().paraDomain()

    def setMesh(self, mesh, ignoreRegionManager=False):

        super(MeshModelling, self).setMesh(mesh, ignoreRegionManager)

    def drawModel(self, ax, model):
        pg.mplviewer.drawModel(ax=ax,
                               mesh=self.paraDomain,
                               data=model,
                               label='Model parameter')
        return ax


class PetroModelling(Modelling):
    """
    Combine petrophysical relation m(p) with modeling class f(p).

    Combine petrophysical relation m(p) with modeling class f(p) to invert
    for m (or any inversion transformation) instead of p.
    """
    def __init__(self, fop, trans, **kwargs):
        """Save forward class and transformation, create Jacobian matrix."""
        mesh = kwargs.pop('mesh', None)

        super(PetroModelling, self).__init__(**kwargs)
        self.fop = fop      # class defining f(p)
        self.trans = trans  # class defining m(p)

        print("Petro_init:", self, self.fop)

        print(self.fop.regionManagerRef())

        if mesh is not None:
            self.setMesh(mesh)

        self.setRegionManager(self.fop.regionManagerRef())

        self._jac = pg.MultRightMatrix(self.fop.jacobian())
        self.setJacobian(self._jac)

        #TODO global TransModel will break RegionConcept
        self._transModel = pg.RTransLogLU()

    def drawModel(self, ax, model):
        self.fop.drawModel(ax, model)

    def response(self, model):
        """Use inverse transformation to get p(m) and compute response."""
        tModel = self.trans(model)
        ret = self.fop.response(tModel)
        return ret

    def createJacobian(self, model):
        """Fill the individual jacobian matrices."""
        self.fop.createJacobian(self.trans(model))
        self._jac.r = self.trans.deriv(model)  # set inner derivative

    def setDataBasis(self, **kwargs):
        self.fop.setDataBasis(**kwargs)

    #def setMesh(self, mesh):
        #"""TODO."""
        #if mesh is None and self.fop.mesh() is None:
            #raise BaseException("Please provide a mesh for "
                                #"this forward operator")

        #if mesh is not None:
            #self.fop.setMesh(mesh)
            #self.fop.createRefinedForwardMesh(refine=False)

        ## self.setMesh(f.mesh(), ignoreRegionManager=True) # not really nessary
        #self.setRegionManager(self.fop.regionManagerRef())


class LCModelling(Modelling):
    """2D Laterally constrained LC modelling.

    2D Laterally constrained LC modelling based on BlockMatrices.
    """
    def __init__(self, fop, **kwargs):
        """Parameters: FDEM data class and number of layers."""

        super(LCModelling, self).__init__(**kwargs)

        self._singleRegion = True

        self._fopTemplate = fop
        self._fops1D = []
        self._mesh = None
        self._nSoundings = 0
        self._parPerSounding = 0
        self._jac = None

        self.soundingPos = None

    def setDataBasis(self, **kwargs):
        """Set homogeneous data basis.

        Set a common data basis to all forward operators.
        If you want individual you need to set them manually.
        """
        for f in self._fops1D:
            f.setDataBasis(**kwargs)

    def createStartModel(self, models, nLayers):
        sm = pg.RVector()
        for i, f in enumerate(self._fops1D):
            sm = pg.cat(sm, f.createStartModel(models[i], nLayers))

        self.setStartModel(sm)
        return sm

    def response(self, par):
        """Cut together forward responses of all soundings."""
        mods = np.asarray(par).reshape(self._nSoundings, self._parPerSounding)

        resp = pg.RVector(0)
        for i in range(self._nSoundings):
            r = self._fops1D[i].response(mods[i])
            #print("i:", i, mods[i], r)
            resp = pg.cat(resp, r)

        return resp

    def createJacobian(self, par):
        """Create Jacobian matrix by creating individual Jacobians."""
        mods = np.asarray(par).reshape(self._nSoundings, self._parPerSounding)

        for i in range(self._nSoundings):
            self._fops1D[i].createJacobian(mods[i])

    def createParametrization(self, nSoundings, nLayers=4, nPar=1):
        """Create LCI mesh and suitable constraints informations.

        Parameters
        ----------
        nLayer : int
            Numbers of depth layers

        nSoundings : int
            Numbers of 1D measurements to laterally constrain

        nPar : int
            Numbers of independent parameter types,
            e.g., nPar = 1 for VES (invert for resisitivies),
            nPar = 2 for VESC (invert for resisitivies and phases)
        """
        nCols = (nPar+1) * nLayers - 1 ## fail for VES-C
        self._parPerSounding = nCols
        self._nSoundings = nSoundings

        self._mesh = pg.createMesh2D(range(nCols + 1),
                                     range(nSoundings + 1))
        self._mesh.rotate(pg.RVector3(0, 0, -np.pi/2))

        cm = np.ones(nCols * nSoundings) * 1

        if not self._singleRegion:
            for i in range(nSoundings):
                for j in range(nPar):
                    cm[i * self._parPerSounding + (j+1) * nLayers-1 :
                    i * self._parPerSounding + (j+2) * nLayers-1] += (j+1)

        self._mesh.setCellMarkers(cm)
        self.setMesh(self._mesh)

        #ax,_=pg.show(self._mesh, self._mesh.cellMarkers(), label='marker')
        #pg.show(self._mesh, ax=ax)

        #ax,_=pg.show(self.regionManager().paraDomain(),
                     #self.regionManager().paraDomain().cellMarkers(), label='pdmarker')
        #pg.show(self.regionManager().paraDomain(), ax=ax)

        #self.createConstraints()

        #pg.mplviewer.drawParameterConstraints(ax, self.regionManager().paraDomain(),
                                              #self.constraints(), cWeight=None)

        #pg.wait()

    def initJacobian(self, dataVals, nLayers):
        """
        Parameters
        ----------
        dataVals : ndarray | RMatrix | list
            Data values of size (nSounding x Data per sounding).
            All data per sounding need to be equal in length.
            If they don't fit into a matrix use list of sounding data.
        """

        nSoundings = len(dataVals)

        #TODO get nPar Infos from fop._fopTemplate
        self.createParametrization(nSoundings, nLayers=nLayers, nPar=1)

        if self._jac is not None:
            self._jac.clear()
        else:
            self._jac = pg.BlockMatrix()

        self.fops1D = []
        nData = 0
        for i in range(nSoundings):
            f = type(self._fopTemplate)(self.verbose)
            f.setMultiThreadJacobian(self._parPerSounding)

            self._fops1D.append(f)

            nID = self._jac.addMatrix(f.jacobian())
            self._jac.addMatrixEntry(nID, nData, self._parPerSounding * i)
            nData += len(dataVals[i])

        self._jac.recalcMatrixSize()
        #print("Jacobian size:", self.J.rows(), self.J.cols(), nData)
        self.setJacobian(self._jac)

    def drawModel(self, ax, model, **kwargs):
        mods = np.asarray(model).reshape(self._nSoundings,
                                         self._parPerSounding)
        nPar = 1
        pg.mplviewer.showStitchedModels(mods, ax=ax, useMesh=True,
                                        x=self.soundingPos,
                                        **kwargs)
