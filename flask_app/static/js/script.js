const detailsBtns = document.querySelectorAll('.details-btn');

detailsBtns.forEach(btn => {
  btn.addEventListener('click', () => {
    const orderId = btn.dataset.orderId;
    const orderDetails = document.querySelector(`.order-details[data-order-id="${orderId}"]`);
    orderDetails.style.display = orderDetails.style.display === 'none' ? 'block' : 'none';
  });
});

$(document).ready(function() {
  $('#sort').change(function() {
    var sortBy = $(this).val();
    $.ajax({
      type: "POST",
      url: "/sort_products/" + category_name,
      data: { sort_by: sortBy },
      success: function(data) {
        $('.product-list').html(data);
      }
    });
  });
});