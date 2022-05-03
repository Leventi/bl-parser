<template>
  <div class="container">
    <div class="row">
      <div class="col-sm-10">
        <h1>Monopoly check</h1>
        <br><br>
        <div>
        <table class="table table-hover">
          <thead>
            <tr>
              <th scope="col">ИНН</th>
              <th scope="col">Реестр</th>
              <th scope="col">Раздел</th>
              <th scope="col">Номер документа</th>
              <th scope="col">Регион</th>
              <th scope="col">Наименование компании</th>
              <th scope="col">Адрес</th>
              <th scope="col">Дата регистрации</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>{{ monopoly.inn }}</td>
              <td>{{ monopoly.registry }}</td>
              <td>{{ monopoly.section }}</td>
              <td>{{ monopoly.docNumber }}</td>
              <td>{{ monopoly.region }}</td>
              <td>{{ monopoly.companyName }}</td>
              <td>{{ monopoly.address }}</td>
              <td>{{ monopoly.dateFirstReg }}</td>
            </tr>
          </tbody>
        </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      monopoly: {},
    };
  },
  methods: {
    getMonopoly() {
      const path = 'http://localhost:8004/api/v1/monopoly_check';
      axios.get(path, {
        params: {
            inn: this.$route.params.inn,
            history: 'true'
        }
      })
        .then(response => {
          this.monopoly = response.data;
        })
        .catch(error => {
          console.error(error);
        });
    },
  },
  created() {
    this.getMonopoly();
  },
};
</script>