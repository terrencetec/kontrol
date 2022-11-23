"""Dynamic mode decomposition class"""
import numpy as np
import scipy


class DMD:
    """Dynamic mode decomposition class"""
    def __init__(self, snapshot_1, snapshot_2=None,
                 truncation_value=None, dt=None, run=True):
        """Constructor

        Parameters
        ---------
        snapshot_1 : array
            The 2-D snapshot array.
        snapshot_2 : array, optional
            The 2-D snapshot array at next time step.
            If not provided, ``snapshot_1[:, :-1]`` becomes snapshot_1 and
            ``snapshot_2[:, 1:]`` becomes ``snapshot_2``.
            Defaults None.
        truncation_value : float, optional
            The truncation value (order/rank) of the system.
            Defaults None.
        dt : float, optional
            The time difference between two snapshots.
            Defaults None.
        run : bool, optional
            Run dynamic mode decomposition upon construction.
            Computes DMD modes, Reduced-order model, etc.
            truncation_value must be specified for this to work.
            Defaults True.
        """
        # Initializing attributes
        self._snapshot_1 = None
        self._snapshot_2 = None
        self._u = None
        self._vh = None
        self._sigma = None
        self._u_truncated = None
        self._vh_truncated = None
        self._sigma_truncated = None
        self._A_reduced = None
        self._w_reduced = None
        self._v_reduced = None
        self._dmd_modes = None
        self._complex_frequencies = None
        self._v_constant = None
        self._time_dynamics = None
        self._dt = None
        self._prediction = None
        self._truncation_value = None

        self.truncation_value = truncation_value
        self.dt = dt

        if snapshot_2 is None:
            self.snapshot_2 = snapshot_1[:, 1:]
            self.snapshot_1 = snapshot_1[:, :-1]
        else:
            self.snapshot_1 = snapshot_1
            self.snapshot_2 = snapshot_2

        if run:
            self.svd()
            self.low_rank_approximation()
            self.compute_reduced_model()
            self.eig_reduced_model()
            self.compute_dmd_modes()
            self.compute_complex_frequencies()

    @property
    def snapshot_1(self):
        """Snapshot 1"""
        return self._snapshot_1

    @snapshot_1.setter
    def snapshot_1(self, _snapshot_1):
        """snapshot_1.setter"""
        self._snapshot_1 = _snapshot_1
        
    @property
    def snapshot_2(self):
        """Snapshot 1"""
        return self._snapshot_2

    @snapshot_2.setter
    def snapshot_2(self, _snapshot_2):
        """snapshot_2.setter"""
        self._snapshot_2 = _snapshot_2
        
    def svd(self):
        """Decompose the snapshot 1
        
        Returns
        -------
        u : array
            Unitary matrix having left singular vectors as columns.
        sigma : array
            The singular values.
        vh : array
            Unitary matrix having right singular vectors as rows.
        """
        u, sigma, vh = scipy.linalg.svd(self.snapshot_1)
        self.u = u
        self.vh = vh
        self.sigma = sigma
        return u, sigma, vh

    @property
    def u(self):
        """Left singular vectors"""
        return self._u

    @u.setter
    def u(self, _u):
        """u.setter"""
        self._u = _u

    @property
    def vh(self):
        """Right singular vectors"""
        return self._vh

    @vh.setter
    def vh(self, _vh):
        """vh.setter"""
        self._vh = _vh

    @property
    def sigma(self):
        """Singular values"""
        return self._sigma

    @sigma.setter
    def sigma(self, _sigma):
        """sigma.setter"""
        self._sigma = _sigma

    def low_rank_approximation(self, truncation_value=None):
        """Truncate the svd.
        
        Paramters
        ---------
        truncation_value : int, optional
            The truncation value (order/rank) of the system.
            Specify as self.truncation_value or via the constuctor option.
            Defaults None.
        
        Returns
        -------
        u_truncated : array
            Truncated unitary matrix having left singular vectors as columns.
        sigma_truncated : array
            Truncated singular values.
        vh_truncated : array
            Truncated unitary matrix having right singular vectors as rows.
        """
        if truncation_value is None:
            if self.truncation_value is None:
                raise ValueError("Please specify truncation_value.")
            truncation_value = self.truncation_value
        else:
            self.truncation_value = truncation_value
        #TODO Add option to automatically select truncation value

        if self.u is None or self.sigma is None or self.vh is None:
            self.svd()

        u_truncated = self.u[:, :truncation_value]
        sigma_truncated = self.sigma[:truncation_value]  # This is a 1-D array.
        sigma_truncated = scipy.linalg.diagsvd(
            sigma_truncated, len(sigma_truncated), len(sigma_truncated))
        vh_truncated = self.vh[:truncation_value, :]
        self.u_truncated = u_truncated
        self.sigma_truncated = sigma_truncated  # This is a square matrix
        self.vh_truncated = vh_truncated
        return u_truncated, sigma_truncated, vh_truncated
    
    @property
    def truncation_value(self):
        """Truncation value (order/rank) of the system"""
        return self._truncation_value

    @truncation_value.setter
    def truncation_value(self, _truncation_value):
        """truncation_value.setter"""
        self._truncation_value = _truncation_value

    @property
    def u_truncated(self):
        """Left singular vectors (truncated)"""
        return self._u_truncated

    @u_truncated.setter
    def u_truncated(self, _u_truncated):
        """u_truncated.setter"""
        self._u_truncated = _u_truncated

    @property
    def vh_truncated(self):
        """Right singular vectors (truncated)"""
        return self._vh_truncated

    @vh_truncated.setter
    def vh_truncated(self, _vh_truncated):
        """vh_truncated.setter"""
        self._vh_truncated = _vh_truncated

    @property
    def sigma_truncated(self):
        """Singular values truncated"""
        return self._sigma_truncated

    @sigma_truncated.setter
    def sigma_truncated(self, _sigma_truncated):
        """sigma_truncated.setter"""
        self._sigma_truncated = _sigma_truncated

    def compute_reduced_model(self):
        """Compute the reduced-order model
        
        Returns
        -------
        A_reduced : array
            Matrix representing the reduced-order model.
        """
        if (self.u_truncated is None or self.vh_truncated is None
                or self.sigma_truncated is None):
            self.low_rank_approximation()

        u_h = self.u_truncated.T.conjugate()
        v = self.vh_truncated.T.conjugate()
        sigma_inv = scipy.linalg.inv(self.sigma_truncated)
        A_reduced = u_h @ self.snapshot_2 @ v @ sigma_inv
        self.A_reduced = A_reduced
        self.eig_reduced_model()  # Compute eigendecomposition as well.
        return A_reduced

    @property
    def A_reduced(self):
        """Reduced-order model"""
        return self._A_reduced

    @A_reduced.setter
    def A_reduced(self, _A_reduced):
        """A_reduced.setter"""
        self._A_reduced = _A_reduced
    
    def eig_reduced_model(self):
        """Eigen decomposition of the reduced-order model

        Returns
        -------
        w_reduced : array
            The list of eigenvalues.
        v_reduced : array
            Eigenvalues as columns.
        """
        if self.A_reduced is None:
            self.compute_reduced_model()

        w_reduced, v_reduced = scipy.linalg.eig(self.A_reduced)
        self.w_reduced = w_reduced
        self.v_reduced = v_reduced
        return w_reduced, v_reduced

    def compute_dmd_modes(self):
        """Compute the DMD modes
        
        Returns
        -------
        dmd_modes : array
            The DMD modes.
        """
        if self.vh_truncated is None or self.sigma_truncated is None:
            self.low_rank_approximation()
        if self.v_reduced is None:
            self.compute_reduced_model()

        v_truncated = self.vh_truncated.T.conjugate()
        sigma_inv = scipy.linalg.inv(self.sigma_truncated)
        # Exact DMD
        dmd_modes = self.snapshot_2 @ v_truncated @ sigma_inv @ self.v_reduced
        # Standard DMD
        # dmd_modes = self.u_truncated @ self.v_reduced
        self.dmd_modes = dmd_modes
        return dmd_modes

    def compute_complex_frequencies(self, dt=None):
        """Compute the complex frequencies

        Parameters
        ----------
        dt : float, optional
            The time spacing between snapshots.
            Specified as self.dt or in constructor option.
            Defaults None.

        Returns
        -------
        complex_frequencies : array
            Array of complex frequencies
        """
        if dt is None:
            if self.dt is None:
                raise ValueError("Please specified dt")
            dt = self.dt
        if self.w_reduced is None:
            self.eig_reduced_model()
            
        complex_frequencies = np.log(self.w_reduced) / dt
        self.complex_frequencies = complex_frequencies
        return complex_frequencies

    @property
    def dt(self):
        """Time difference between the snapshots"""
        return self._dt

    @dt.setter
    def dt(self, _dt):
        """dt.setter"""
        self._dt = _dt

    def predict(self, t):
        """Predict the future states given a time array
        
        Parameters
        ----------
        t : array
            The time array

        Returns
        -------
        prediction : array
            Predicted states.
        """
        # Make complex frequencies into a diagonal matrix.
        diag_complex_frequencies = np.diag(self.complex_frequencies)
        
        # Expand the array into another dimension as time series.
        complex_frequencies_series = np.repeat(
            diag_complex_frequencies[:, :, np.newaxis], len(t), axis=2)
        
        # Compute the exponentials.
        exponentials = np.exp(complex_frequencies_series * t)

        # Clear the non-diagonal elementes
        # I need to understand how the following diagonalization code works.
        diag = np.einsum("iik->ik", exponentials)
        save = diag.copy()
        exponentials[...] = 0
        diag[...] = save
        # exponentials is diagonalized.
        
        # Compute the constant vector.
        # Assume t=0 at snapshot[:, 0].
        v_constant, _, _, _ = np.linalg.lstsq(
            self.dmd_modes, self.snapshot_1[:, 0], rcond=None)
        # Assume t=t[0] at snapshot[:, 0].
        # v_constant, _, _, _ = np.linalg.lstsq(
        #     self.dmd_modes @ np.diag(np.exp(self.complex_frequencies*t[0])),
        #     self.snapshot_1[:, 0], rcond=None)
        self.v_constant = v_constant
        
        # Compute time dynamics exp(omega*t) @ b
        time_dynamics = np.einsum("ijk,j->ik", exponentials, v_constant)
        self.time_dynamics = time_dynamics

        # Prediction = dmd_modes @ exp(omega*t) @ b
        prediction = self.dmd_modes @ self.time_dynamics
        self.prediction = prediction

        return prediction

    @property
    def v_constant(self):
        """Constant vector of the ODE solution"""
        return self._v_constant

    @v_constant.setter
    def v_constant(self, _v_constant):
        """v_constant.setter"""
        self._v_constant = _v_constant

    @property
    def time_dynamics(self):
        """Time dynamics of the ODE solution"""
        return self._time_dynamics

    @time_dynamics.setter
    def time_dynamics(self, _time_dynamics):
        """time_dynamics.setter"""
        self._time_dynamics = _time_dynamics

    @property
    def prediction(self):
        """The ODE solution"""
        return self._prediction

    @prediction.setter
    def prediction(self, _prediction):
        """prediction.setter"""
        self._prediction = _prediction
