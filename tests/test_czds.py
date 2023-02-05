"""Testing the main CZDS class."""


def test_czds_base_variables(main_class):
    """Testing to ensure that the CZDS parameters are stored correctly."""
    from czds.base import Base

    data = {"username": "test.name@nothing.xyz", "password": "testpassword1!", "save_directory": "./"}
    main_class(**data)

    assert Base.USERNAME == data["username"]
    assert Base.PASSWORD == data["password"]
    assert Base.SAVE_PATH == data["save_directory"]
