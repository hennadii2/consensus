import time

import apache_beam as beam  # type: ignore


class TestFn(beam.DoFn):
    def __init__(self):
        self.window = beam.transforms.window.GlobalWindow()

    def start_bundle(self):
        self.list = []

    def finish_bundle(self):
        for elem, ts in self.list:
            yield beam.utils.windowed_value.WindowedValue(
                value=elem,
                timestamp=ts,
                windows=[self.window],
            )

    def process(self, data, timestamp=beam.DoFn.TimestampParam, window=beam.DoFn.WindowParam):
        self.window = window
        self.list.append((data, timestamp))


def main(argv=None):
    print("hello world")

    with beam.Pipeline() as p:
        results = (
            p
            | "CreateData" >> beam.Create(map(str, range(1, 100)))
            | "WithTimestamps" >> beam.Map(lambda x: beam.window.TimestampedValue(x, time.time()))
            | "TestFn" >> beam.ParDo(TestFn())
            | "Print" >> beam.Map(print)
        )

        print(results)


if __name__ == "__main__":
    main()
