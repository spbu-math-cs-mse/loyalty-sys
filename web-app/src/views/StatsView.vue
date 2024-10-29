<script setup>
import { ref, onMounted } from "vue";
import Chart from "primevue/chart";
import ViewSectionHeaderInfo from "@/components/ViewSectionHeaderInfo.vue";
import ChartNumberDisplay from "@/components/ChartNumberDisplay.vue";

onMounted(() => {
  chartOptions.value = setChartOptions();
  chartConfig.value = setChartConfig();
});

let chartData = ref();

const chartOptions = ref();
const chartConfig = ref();
const flag = ref(1);

const setChartConfig = () => {
  return {
    id: "customCanvasBackgroundColor",
    beforeDraw: (chart, args, options) => {
      const { ctx } = chart;
      ctx.save();
      ctx.globalCompositeOperation = "destination-over";
      ctx.fillStyle = options.color || "#fff";
      ctx.fillRect(0, 0, chart.width, chart.height);
      ctx.restore();
    },
  };
};

const setChartData = () => {
  const documentStyle = getComputedStyle(document.body);

  switch (flag.value) {
    case 1:
      chartData = {
        labels: ["Мужчины", "Женщины", "Неизвестно"],
        datasets: [
          {
            data: [540, 625, 152],
            backgroundColor: [
              documentStyle.getPropertyValue("--p-cyan-500"),
              documentStyle.getPropertyValue("--p-orange-500"),
              documentStyle.getPropertyValue("--p-gray-500"),
            ],
            hoverBackgroundColor: [
              documentStyle.getPropertyValue("--p-cyan-400"),
              documentStyle.getPropertyValue("--p-orange-400"),
              documentStyle.getPropertyValue("--p-gray-400"),
            ],
            borderRadius: 2,
          },
        ],
      };
      break;

    case 2:
      chartData = {
        labels: ["Мужчины", "Женщины", "Хз.. Кто-то"],
        datasets: [
          {
            data: [1540, 2625, 10152],
            backgroundColor: [
              documentStyle.getPropertyValue("--p-cyan-500"),
              documentStyle.getPropertyValue("--p-orange-500"),
              documentStyle.getPropertyValue("--p-gray-500"),
            ],
            hoverBackgroundColor: [
              documentStyle.getPropertyValue("--p-cyan-400"),
              documentStyle.getPropertyValue("--p-orange-400"),
              documentStyle.getPropertyValue("--p-gray-400"),
            ],
            borderRadius: 2,
          },
        ],
      };
      break;

    default:
      chartData = {
        labels: ["Мужчины", "Женщины", "В душе не чаю кто ты, Воин!"],
        datasets: [
          {
            data: [100, 62500, 1],
            backgroundColor: [
              documentStyle.getPropertyValue("--p-cyan-500"),
              documentStyle.getPropertyValue("--p-orange-500"),
              documentStyle.getPropertyValue("--p-gray-500"),
            ],
            hoverBackgroundColor: [
              documentStyle.getPropertyValue("--p-cyan-400"),
              documentStyle.getPropertyValue("--p-orange-400"),
              documentStyle.getPropertyValue("--p-gray-400"),
            ],
            borderRadius: 2,
          },
        ],
      };
  }

  return chartData;
};

// const changeChartOptionsTitle = (_options, _title) => {
//   const reactiveOptions = reactive(_options);
//   console.log(reactiveOptions);
//   reactiveOptions.plugins.title.text = title;
//   return reactiveOptions;
// };

const setChartOptions = () => {
  const documentStyle = getComputedStyle(document.documentElement);
  const textColor = documentStyle.getPropertyValue("--p-text-color");
  const backgroundColor = documentStyle.getPropertyValue("--p-menu-background");

  return {
    plugins: {
      legend: {
        labels: {
          usePointStyle: true,
          color: textColor,
          font: {
            family: "Montserrat",
            size: 12,
          },
        },
      },
      title: {
        display: true,
        text: "Кто чаще покупает",
        align: "start",
        color: textColor,
        padding: 8,
        font: {
          size: 18,
          family: "Montserrat",
          weight: 600,
        },
      },
      customCanvasBackgroundColor: {
        color: backgroundColor,
      },
      tooltip: {
        titleFont: {
          family: "Montserrat",
          weight: 400,
        },
        bodyFont: {
          family: "Montserrat",
          weight: 400,
        },
      },
    },
    layout: {
      padding: {
        top: 10,
        bottom: 10,
        left: 15,
        right: 10,
      },
    },
    responsive: true,
    aspectRatio: 2,
    maintainAspectRatio: false,
    responsiveAnimationDuration: 0,
  };
};
</script>

<template>
  <div class="about lg:py-4 py-1 md:pl-3 pl-0">
    <ViewSectionHeaderInfo title="Статистика" />

    <div
      class="flex flex-wrap justify-content-around lg:justify-content-start gap-4"
    >
      <div class="border-round-lg overflow-hidden shadow-1">
        <Chart
          type="doughnut"
          :width="500"
          :height="300"
          :data="setChartData()"
          :plugins="[chartConfig]"
          :options="chartOptions"
          class=""
        />
      </div>
      <div class="flex flex-column gap-4 w-full lg:w-auto">
        <ChartNumberDisplay
          title="Cумма покупок"
          number="231654.00"
          money="₽"
          afterIcon="pi-arrow-down-right"
        />
        <ChartNumberDisplay
          title="Средний чек"
          number="4990.00"
          money="₽"
          afterIcon="pi-arrow-up-right"
        />
        <ChartNumberDisplay
          title="Поситители"
          number="546"
          beforeIcon="pi-users"
        />
      </div>
    </div>
  </div>
</template>
