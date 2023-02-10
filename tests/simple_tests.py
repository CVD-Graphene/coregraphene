def test_kwargs():
    def a(**kwargs):
        d = {"v": 1}
        d.update(kwargs)
        return d

    def a2(**kwargs):
        print("A2 kwargs", kwargs)

    def b():
        ans_a = a(h=1, v=3, g=5)
        a2(**ans_a)

    b()


if __name__ == '__main__':
    test_kwargs()
