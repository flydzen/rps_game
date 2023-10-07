<script>
export default {
    name: "LeaderBoardItem",
    props: {
        item: {
            type: Object,
            required: true
        },
        user: {
            type: String,

        }
    }
}
</script>

<template>
    <tr>
        <th> {{ item.position }}</th>
        <th> {{ item.login }}</th>
        <th> {{ item.victories }}</th>
        <th> {{ item.losses }}</th>
    </tr>
</template>

<style scoped>
th, td {
    border: 2px solid #2e2e31;
    text-align: left;
    padding: 8px;
    border-radius: 1px;
}

th {
    background-color: #3E3C3C;
}
</style>