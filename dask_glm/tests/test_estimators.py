import pytest

from dask_glm.estimators import LogisticRegression, LinearRegression
from dask_glm.datasets import make_classification, make_regression
from dask_glm.algorithms import _solvers
from dask_glm.regularizers import _regularizers


@pytest.fixture(params=_solvers.keys())
def solver(request):
    """Parametrized fixture for all the solver names"""
    return request.param


@pytest.fixture(params=_regularizers.keys())
def regularizer(request):
    """Parametrized fixture for all the regularizer names"""
    return request.param


class DoNothingTransformer(object):
    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        return X

    def fit_transform(self, X, y=None):
        return X

    def get_params(self, deep=True):
        return {}


X, y = make_classification()


def test_lr_init(solver):
    LogisticRegression(solver=solver)


@pytest.mark.parametrize('fit_intercept', [True, False])
def test_fit(fit_intercept):
    X, y = make_classification(n_samples=100, n_features=5, chunksize=10)
    lr = LogisticRegression(fit_intercept=fit_intercept)
    lr.fit(X, y)
    lr.predict(X)
    lr.predict_proba(X)


@pytest.mark.parametrize('fit_intercept', [True, False])
def test_lm(fit_intercept):
    X, y = make_regression(n_samples=100, n_features=5, chunksize=10)
    lr = LinearRegression(fit_intercept=fit_intercept)
    lr.fit(X, y)
    lr.predict(X)
    if fit_intercept:
        assert lr.intercept_ is not None


@pytest.mark.parametrize('fit_intercept', [True, False])
def test_big(fit_intercept):
    import dask
    dask.set_options(get=dask.get)
    X, y = make_classification()
    lr = LogisticRegression(fit_intercept=fit_intercept)
    lr.fit(X, y)
    lr.predict(X)
    lr.predict_proba(X)
    if fit_intercept:
        assert lr.intercept_ is not None


def test_in_pipeline():
    from sklearn.pipeline import make_pipeline
    X, y = make_classification(n_samples=100, n_features=5, chunksize=10)
    pipe = make_pipeline(DoNothingTransformer(), LogisticRegression())
    pipe.fit(X, y)


def test_gridsearch():
    from sklearn.pipeline import make_pipeline
    dcv = pytest.importorskip('dask_searchcv')

    X, y = make_classification(n_samples=100, n_features=5, chunksize=10)
    grid = {
        'logisticregression__lamduh': [.001, .01, .1, .5]
    }
    pipe = make_pipeline(DoNothingTransformer(), LogisticRegression())
    search = dcv.GridSearchCV(pipe, grid, cv=3)
    search.fit(X, y)
