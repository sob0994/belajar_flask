const regModal = (elid) => {
  const lokasi = document.getElementsByTagName("body")[0];
  const modal = document.querySelector(elid);
  lokasi.appendChild(modal);
  var modals = modal.querySelectorAll("[close-modal]");
  modals.forEach((m) => {
    m.addEventListener("click", () => {
      modal.classList.toggle("open");
    });
  });
  document.querySelectorAll("[open-modal]").forEach((dt) => {
    dt.addEventListener("click", () => {
      let mdl = document.querySelector(dt.getAttribute("open-modal"));
      if (mdl) {
        mdl.classList.toggle("open");
      }
    });
  });
};
