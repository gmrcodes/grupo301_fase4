# Aquí va el código desarrollado para la Fase 4 del curso
# de programación 2013023. El grupo 301 está integrado por:
# Alith Rodríguez, Germán Riveros

"""Sistema Integral de Gestión de Clientes, Servicios y Reservas - Software FJ.

Módulo único orientado a objetos que implementa abstracción, herencia,
polimorfismo, encapsulación y manejo avanzado de excepciones sin base de datos.
"""

from abc import ABC, abstractmethod
from enum import Enum
import logging
from typing import Any, overload
import re


# ==========================================
# 1. Configuración del Sistema de Logs
# ==========================================

def configure_logging(log_file: str = "software_fj.log") -> logging.Logger:
    """Configura y retorna el logger principal de la aplicación.

    Args:
        log_file: Ruta o nombre del archivo donde se almacenarán los eventos.

    Returns:
        Instancia configurada de logging.Logger.
    """
    logger = logging.getLogger("SoftwareFJ")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        file_handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


LOGGER = configure_logging()


# ==========================================
# 2. Jerarquía de Excepciones Personalizadas
# ==========================================

class SoftwareFJError(Exception):
    """Excepción base para todos los errores de dominio en Software FJ."""


class InvalidEntityError(SoftwareFJError):
    """Se lanza cuando los identificadores o atributos base son inválidos."""


class InvalidClientError(SoftwareFJError):
    """Se lanza ante datos inválidos o inconsistentes en un cliente."""


class InvalidServiceError(SoftwareFJError):
    """Se lanza ante parámetros inválidos o indisponibilidad de un servicio."""


class ReservationError(SoftwareFJError):
    """Se lanza cuando una reserva falla en validación, cálculo o estado."""


# ==========================================
# 3. Clase Abstracta Base del Sistema
# ==========================================

class BaseEntity(ABC):
    """Clase abstracta que representa cualquier entidad identificable del sistema."""

    def __init__(self, entity_id: str) -> None:
        """Inicializa la entidad validando su identificador único.

        Args:
            entity_id: Cadena no vacía que identifica de forma única la entidad.

        Raises:
            InvalidEntityError: Si el identificador no es una cadena válida.
        """
        self._entity_id: str = self._validate_id(entity_id)

    @staticmethod
    def _validate_id(entity_id: Any) -> str:
        """Valida que el identificador sea un texto no vacío ni compuesto solo por espacios.

        Args:
            entity_id: Valor a validar como identificador.

        Returns:
            El identificador limpio de espacios en los extremos.

        Raises:
            InvalidEntityError: Si el valor es nulo, no es str o está vacío.
        """
        if not isinstance(entity_id, str) or not entity_id.strip():
            raise InvalidEntityError(
                f"Identificador de entidad inválido: '{entity_id}'. Debe ser una cadena no vacía."
            )
        return entity_id.strip()

    @property
    def entity_id(self) -> str:
        """Retorna el identificador encapsulado de solo lectura de la entidad."""
        return self._entity_id

    @abstractmethod
    def get_details(self) -> str:
        """Retorna una representación detallada en texto de la entidad."""
        raise NotImplementedError

    def __str__(self) -> str:
        """Representación legible estándar delegada a get_details."""
        return self.get_details()
    
# ================================================
# 4. Clase cliente (Encapsulamiento y validaciones)
# ================================================

class Client(BaseEntity):
    """Representa un cliente de Software FJ con validación estricta de datos."""

    _EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

    def __init__(self, client_id: str, name: str, email: str) -> None:
        """Inicializa un cliente validando su ID, nombre y correo electrónico.

        Args:
            client_id: Identificador único del cliente.
            name: Nombre completo (mínimo 3 caracteres alfabéticos/espacios).
            email: Dirección de correo electrónico con formato válido.

        Raises:
            InvalidEntityError: Si el ID es inválido.
            InvalidClientError: Si el nombre o el correo no cumplen las reglas.
        """
        super().__init__(client_id)
        self.name = name
        self.email = email

    @property
    def name(self) -> str:
        """Retorna el nombre encapsulado del cliente."""
        return self._name

    @name.setter
    def name(self, value: Any) -> None:
        """Valida y asigna el nombre del cliente.

        Args:
            value: Nuevo nombre a asignar.

        Raises:
            InvalidClientError: Si no es texto o tiene menos de 3 caracteres reales.
        """
        if not isinstance(value, str) or len(value.strip()) < 3:
            raise InvalidClientError(
                f"Nombre de cliente inválido: '{value}'. Debe contener al menos 3 caracteres."
            )
        self._name: str = value.strip()

    @property
    def email(self) -> str:
        """Retorna el correo electrónico encapsulado del cliente."""
        return self._email

    @email.setter
    def email(self, value: Any) -> None:
        """Valida y asigna el correo electrónico mediante expresión regular.

        Args:
            value: Dirección de correo a validar.

        Raises:
            InvalidClientError: Si el correo no es texto o incumple el formato estándar.
        """
        if not isinstance(value, str) or not self._EMAIL_PATTERN.match(value.strip()):
            raise InvalidClientError(
                f"Correo electrónico inválido: '{value}'. Formato esperado: usuario@dominio.ext"
            )
        self._email: str = value.strip().lower()

    def get_details(self) -> str:
        """Retorna la ficha formateada del cliente."""
        return f"Client[ID: {self.entity_id}] | Name: {self.name} | Email: {self.email}"
    
# =======================================
# 5. Clase abstracta servicio y subclases
# =======================================
    
class Service(BaseEntity, ABC):
    """Clase abstracta base para los servicios ofrecidos por Software FJ."""

    def __init__(
        self,
        service_id: str,
        name: str,
        base_rate: float,
        available: bool = True,
    ) -> None:
        """Inicializa un servicio validando nombre, tarifa y disponibilidad.

        Args:
            service_id: Identificador único del servicio.
            name: Nombre del servicio.
            base_rate: Tarifa base por unidad de tiempo (debe ser mayor a 0).
            available: Indica si el servicio está habilitado para reservas.

        Raises:
            InvalidServiceError: Si el nombre, tarifa o disponibilidad son inválidos.
        """
        super().__init__(service_id)
        self.name = name
        self.base_rate = base_rate
        self.available = available

    @property
    def name(self) -> str:
        """Retorna el nombre del servicio."""
        return self._name

    @name.setter
    def name(self, value: Any) -> None:
        """Valida que el nombre del servicio sea una cadena no vacía."""
        if not isinstance(value, str) or len(value.strip()) < 3:
            raise InvalidServiceError(
                f"Nombre de servicio inválido: '{value}'. Mínimo 3 caracteres."
            )
        self._name: str = value.strip()

    @property
    def base_rate(self) -> float:
        """Retorna la tarifa base del servicio."""
        return self._base_rate

    @base_rate.setter
    def base_rate(self, value: Any) -> None:
        """Valida y convierte la tarifa base asegurando un valor estrictamente positivo."""
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise InvalidServiceError(
                f"La tarifa base debe ser numérica, se recibió: '{value}'."
            )
        if value <= 0:
            raise InvalidServiceError(
                f"La tarifa base debe ser mayor a cero, se recibió: {value}."
            )
        self._base_rate: float = float(value)

    @property
    def available(self) -> bool:
        """Indica si el servicio está disponible actualmente."""
        return self._available

    @available.setter
    def available(self, value: Any) -> None:
        """Valida que la disponibilidad sea estrictamente booleana."""
        if not isinstance(value, bool):
            raise InvalidServiceError("El estado de disponibilidad debe ser booleano (True/False).")
        self._available: bool = value

    def _validate_calculation_inputs(
        self,
        duration: Any,
        tax_rate: float,
        discount_rate: float,
        extra_charge: float,
    ) -> int:
        """Valida los parámetros comunes antes de ejecutar cualquier cálculo de costo.

        Args:
            duration: Unidades de tiempo (horas o días).
            tax_rate: Porcentaje de impuesto en formato decimal (ej. 0.19).
            discount_rate: Porcentaje de descuento en formato decimal (0.0 a 0.99).
            extra_charge: Cargo adicional no negativo (seguro, bono o logística).

        Returns:
            La duración validada como entero positivo.

        Raises:
            InvalidServiceError: Si el servicio no está disponible o algún parámetro es inválido.
        """
        if not self.available:
            raise InvalidServiceError(
                f"El servicio '{self.name}' ({self.entity_id}) no está disponible actualmente."
            )
        if isinstance(duration, bool) or not isinstance(duration, int) or duration <= 0:
            raise InvalidServiceError(
                f"Duración inválida: '{duration}'. Debe ser un entero mayor a cero."
            )
        if not isinstance(tax_rate, (int, float)) or tax_rate < 0:
            raise InvalidServiceError(f"Tasa de impuesto inválida: {tax_rate}.")
        if not isinstance(discount_rate, (int, float)) or not (0.0 <= discount_rate < 1.0):
            raise InvalidServiceError(
                f"Descuento inválido: {discount_rate}. Debe estar entre 0.0 y 0.99."
            )
        if not isinstance(extra_charge, (int, float)) or extra_charge < 0:
            raise InvalidServiceError(f"Cargo adicional inválido: {extra_charge}.")
        return duration

    @overload
    def calculate_cost(self, duration: int) -> float: ...

    @overload
    def calculate_cost(self, duration: int, tax_rate: float) -> float: ...

    @overload
    def calculate_cost(
        self,
        duration: int,
        tax_rate: float = 0.19,
        discount_rate: float = 0.0,
        extra_charge: float = 0.0,
    ) -> float: ...

    @abstractmethod
    def calculate_cost(
        self,
        duration: int,
        tax_rate: float = 0.19,
        discount_rate: float = 0.0,
        extra_charge: float = 0.0,
    ) -> float:
        """Calcula el costo total del servicio aplicando reglas propias de cada subclase."""
        raise NotImplementedError

    @abstractmethod
    def get_description(self) -> str:
        """Retorna la descripción comercial y técnica específica del servicio."""
        raise NotImplementedError

    def get_details(self) -> str:
        """Retorna los detalles generales del servicio."""
        status = "Disponible" if self.available else "No disponible"
        return (
            f"Service[ID: {self.entity_id}] | {self.name} | "
            f"Base Rate: ${self.base_rate:,.2f} | Status: {status}"
        )


class RoomService(Service):
    """Servicio especializado para reserva de salas físicas o auditorios."""

    def __init__(
        self,
        service_id: str,
        name: str,
        base_rate: float,
        capacity: int,
        available: bool = True,
    ) -> None:
        """Inicializa una sala validando su aforo máximo."""
        super().__init__(service_id, name, base_rate, available)
        self.capacity = capacity

    @property
    def capacity(self) -> int:
        """Retorna la capacidad máxima de personas de la sala."""
        return self._capacity

    @capacity.setter
    def capacity(self, value: Any) -> None:
        """Valida que la capacidad sea un entero mayor a cero."""
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise InvalidServiceError(
                f"Capacidad de sala inválida: '{value}'. Debe ser un entero positivo."
            )
        self._capacity: int = value

    def get_description(self) -> str:
        """Retorna la descripción detallada de la sala."""
        return (
            f"Room Service: {self.name} | Capacity: {self.capacity} people | "
            f"Hourly Rate: ${self.base_rate:,.2f}"
        )

    def calculate_cost(
        self,
        duration: int,
        tax_rate: float = 0.19,
        discount_rate: float = 0.0,
        extra_charge: float = 0.0,
    ) -> float:
        """Calcula el costo de la sala aplicando descuento por volumen y recargo de montaje."""
        valid_duration = self._validate_calculation_inputs(
            duration, tax_rate, discount_rate, extra_charge
        )
        # Descuento automático adicional del 5% si la reserva supera las 8 horas
        effective_discount = min(0.99, discount_rate + (0.05 if valid_duration >= 8 else 0.0))
        discounted_base = (self.base_rate * valid_duration) * (1.0 - effective_discount)
        subtotal = discounted_base + extra_charge
        return round(subtotal * (1.0 + tax_rate), 2)


class EquipmentService(Service):
    """Servicio especializado para alquiler de equipos tecnológicos."""

    def __init__(
        self,
        service_id: str,
        name: str,
        base_rate: float,
        hardware_type: str,
        available: bool = True,
    ) -> None:
        """Inicializa un equipo validando su categoría de hardware."""
        super().__init__(service_id, name, base_rate, available)
        self.hardware_type = hardware_type

    @property
    def hardware_type(self) -> str:
        """Retorna el tipo de hardware del equipo."""
        return self._hardware_type

    @hardware_type.setter
    def hardware_type(self, value: Any) -> None:
        """Valida que el tipo de hardware sea una cadena no vacía."""
        if not isinstance(value, str) or not value.strip():
            raise InvalidServiceError("El tipo de hardware no puede estar vacío.")
        self._hardware_type: str = value.strip()

    def get_description(self) -> str:
        """Retorna la descripción detallada del equipo en alquiler."""
        return (
            f"Equipment Rental: {self.name} [{self.hardware_type}] | "
            f"Daily Rate: ${self.base_rate:,.2f}"
        )

    def calculate_cost(
        self,
        duration: int,
        tax_rate: float = 0.19,
        discount_rate: float = 0.0,
        extra_charge: float = 50.0,
    ) -> float:
        """Calcula el costo del equipo sumando póliza de seguro diaria por defecto ($50)."""
        valid_duration = self._validate_calculation_inputs(
            duration, tax_rate, discount_rate, extra_charge
        )
        discounted_base = (self.base_rate * valid_duration) * (1.0 - discount_rate)
        # En equipos, extra_charge representa el seguro obligatorio por cada día de alquiler
        insurance_total = extra_charge * valid_duration
        subtotal = discounted_base + insurance_total
        return round(subtotal * (1.0 + tax_rate), 2)


class AdvisoryService(Service):
    """Servicio especializado para consultorías y asesorías técnicas."""

    def __init__(
        self,
        service_id: str,
        name: str,
        base_rate: float,
        specialty: str,
        available: bool = True,
    ) -> None:
        """Inicializa una asesoría validando el área de especialidad."""
        super().__init__(service_id, name, base_rate, available)
        self.specialty = specialty

    @property
    def specialty(self) -> str:
        """Retorna el área de especialidad de la asesoría."""
        return self._specialty

    @specialty.setter
    def specialty(self, value: Any) -> None:
        """Valida que la especialidad sea una cadena no vacía."""
        if not isinstance(value, str) or not value.strip():
            raise InvalidServiceError("La especialidad de la asesoría no puede estar vacía.")
        self._specialty: str = value.strip()

    def get_description(self) -> str:
        """Retorna la descripción detallada de la asesoría."""
        return (
            f"Specialized Advisory: {self.name} (Specialty: {self.specialty}) | "
            f"Hourly Rate: ${self.base_rate:,.2f}"
        )

    def calculate_cost(
        self,
        duration: int,
        tax_rate: float = 0.19,
        discount_rate: float = 0.0,
        extra_charge: float = 0.0,
    ) -> float:
        """Calcula el costo de asesoría aplicando bono por entregables/viáticos (extra_charge)."""
        valid_duration = self._validate_calculation_inputs(
            duration, tax_rate, discount_rate, extra_charge
        )
        discounted_base = (self.base_rate * valid_duration) * (1.0 - discount_rate)
        subtotal = discounted_base + extra_charge
        return round(subtotal * (1.0 + tax_rate), 2)
    
# ====================
# 6. Clase de reserva
# ====================

class ReservationStatus(Enum):
    """Estados válidos dentro del ciclo de vida de una reserva."""

    PENDING = "Pending"
    CONFIRMED = "Confirmed"
    CANCELLED = "Cancelled"
    FAILED = "Failed"


class Reservation(BaseEntity):
    """Integra cliente, servicio y duración gestionando el ciclo de vida de la reserva."""

    _id_counter: int = 1000

    def __init__(
        self,
        client: Client,
        service: Service,
        duration: int,
        tax_rate: float = 0.19,
        discount_rate: float = 0.0,
        extra_charge: float = 0.0,
    ) -> None:
        """Inicializa una reserva en estado pendiente validando sus entidades asociadas.

        Args:
            client: Instancia válida de Client que solicita el servicio.
            service: Instancia válida de una subclase de Service.
            duration: Cantidad de horas o días solicitados.
            tax_rate: Tasa de impuesto aplicable en decimal.
            discount_rate: Descuento promocional en decimal (0.0 a 0.99).
            extra_charge: Cargo adicional opcional (seguro, bono o montaje).

        Raises:
            ReservationError: Si el cliente o el servicio no son instancias válidas.
        """
        if not isinstance(client, Client):
            raise ReservationError("La reserva requiere una instancia válida de Client.")
        if not isinstance(service, Service):
            raise ReservationError("La reserva requiere una instancia válida de Service.")

        Reservation._id_counter += 1
        super().__init__(f"RES-{Reservation._id_counter}")

        self._client: Client = client
        self._service: Service = service
        self._duration: int = duration
        self._tax_rate: float = tax_rate
        self._discount_rate: float = discount_rate
        self._extra_charge: float = extra_charge
        self._status: ReservationStatus = ReservationStatus.PENDING
        self._total_cost: float = 0.0

    @property
    def client(self) -> Client:
        """Retorna el cliente asociado a la reserva."""
        return self._client

    @property
    def service(self) -> Service:
        """Retorna el servicio asociado a la reserva."""
        return self._service

    @property
    def duration(self) -> int:
        """Retorna la duración solicitada."""
        return self._duration

    @property
    def status(self) -> ReservationStatus:
        """Retorna el estado actual de la reserva."""
        return self._status

    @property
    def total_cost(self) -> float:
        """Retorna el costo total calculado tras procesar la reserva."""
        return self._total_cost

    def process(self) -> float:
        """Procesa y confirma la reserva calculando su costo de forma polimórfica.

        Returns:
            El costo total confirmado de la reserva.

        Raises:
            ReservationError: Si la reserva no está pendiente, si el servicio falla
                en sus validaciones o si ocurre un error inesperado.
        """
        # Guardia de estado fuera del try para no corromper reservas ya confirmadas
        if self._status is not ReservationStatus.PENDING:
            msg = (
                f"Operación no permitida: la reserva {self.entity_id} ya fue procesada "
                f"(estado actual: {self._status.value})."
            )
            LOGGER.warning(msg)
            raise ReservationError(msg)

        try:
            LOGGER.info(
                "Procesando reserva %s | Cliente: %s | Servicio: %s",
                self.entity_id,
                self._client.name,
                self._service.name,
            )
            # Llamada polimórfica sin necesidad de verificar el tipo de subclase
            self._total_cost = self._service.calculate_cost(
                duration=self._duration,
                tax_rate=self._tax_rate,
                discount_rate=self._discount_rate,
                extra_charge=self._extra_charge,
            )
        except InvalidServiceError as exc:
            self._status = ReservationStatus.FAILED
            LOGGER.error("Fallo de validación en reserva %s: %s", self.entity_id, exc)
            raise ReservationError(
                f"No se pudo confirmar la reserva {self.entity_id}: {exc}"
            ) from exc
        except Exception as exc:
            self._status = ReservationStatus.FAILED
            LOGGER.critical(
                "Error inesperado procesando reserva %s: %s", self.entity_id, exc
            )
            raise ReservationError(
                f"Error crítico inesperado al procesar {self.entity_id}."
            ) from exc
        else:
            self._status = ReservationStatus.CONFIRMED
            LOGGER.info(
                "Reserva %s confirmada exitosamente. Total: $%.2f",
                self.entity_id,
                self._total_cost,
            )
            return self._total_cost
        finally:
            LOGGER.info(
                "Auditoría de cierre -> Reserva %s finalizó intento con estado: %s",
                self.entity_id,
                self._status.value,
            )

    def cancel(self) -> None:
        """Cancela una reserva únicamente si se encuentra en estado confirmado.

        Raises:
            ReservationError: Si se intenta cancelar una reserva que no está confirmada.
        """
        try:
            if self._status is not ReservationStatus.CONFIRMED:
                raise ReservationError(
                    f"Operación no permitida: no se puede cancelar la reserva {self.entity_id} "
                    f"en estado '{self._status.value}'."
                )
        except ReservationError as exc:
            LOGGER.warning("Intento inválido de cancelación: %s", exc)
            raise
        else:
            self._status = ReservationStatus.CANCELLED
            LOGGER.info("Reserva %s cancelada exitosamente.", self.entity_id)

    def get_details(self) -> str:
        """Retorna el resumen completo de la reserva y su estado actual."""
        return (
            f"Reservation[ID: {self.entity_id}] | Client: {self._client.name} | "
            f"Service: {self._service.name} | Duration: {self._duration} | "
            f"Status: {self._status.value} | Total: ${self._total_cost:,.2f}"
        )
            
# =================================
# 7. Simulación de diez operaciones
# =================================

if __name__ == "__main__":
    print("=== Simulación de Operaciones del Sistema de Reservas ===")
    
    
    clientes_registrados = []
    servicios_disponibles = []
    historial_reservas = []
    
    #Operación 1: Registro de cliente 1
    try:
        c1 = Client("CLI-01", "Juan Pérez", "juan.perez@email.com")
        clientes_registrados.append(c1)
        print(f"1. Registro exitoso: {c1.details()}")
        logging.info(f"Cliente registrado: {c1.name}")
    except Exception as e:
        print(f"Error al registrar cliente: {e}")
    
    #Operación 2: Registro fallido del cliente (nombre invalido)
    try:
        print("\n2. Intentando registrar cliente con nombre invalido")
        c_malo = Client("CLI-02", "All", "all@email.com")
    except InvalidClientError as cie:
        print(f"Excepcion capturada: {cie}")
        logging.warning(f"Intento de registro fallido: {cie}")
        
    # Operación 3: Registro de cliente 2
    try: 
        c2 = Client("CLI-03", "María López", "maria.lopez@email.com")
        clientes_registrados.append(c2)
        print(f"\n3. Registro exitoso: {c2.detalles()}")
    except Exception as e:
        print(f"Error: {e}")
    
    #Operación 4: Registro de servicio de sala
    try: 
        s1 = RoomService("SRV-01", "Sala Magna", 45000.0, 20)
        servicios_disponibles.append(s1)
        print(f"\n4. Servicio registrado: {s1.descripcion()}")
    except Exception as e:
        print(f"Error: {e}")
    
    #Operación 5: Registro de servicio de asesoría
    try:
        s2 = AdvisoryService("SRV-02", "Servidor Cloud AWS", 120000.0, "Servidor Dedicado")
        servicios_disponibles.append(s2)
        print(f"\n5. Servicio registrado: {s2.descripcion()}")
    except Exception as e:
        print(f"Error: {e}")
        
    #Operación 6: Creación correcta de servicio 
    try:
        s3 = AdvisoryService("SRV-03", "Consultoria en Machine Learning", 90000.0, "Inteligencia Artificial")
        servicios_disponibles.append(s3)
        print(f"\n6. Servicio registrado: {s3.descripcion()}")
    except Exception as e:
        print(f"Error: {e}")
        
    #Operación 7: Reserva Exitosa 1
    try:
        print("\n7. Procesando reserva 1 (Sala magna por 4 horas con 10% de descuento)")
        res1 = Reserva(clientes_registrados[0], servicios_disponibles[0], 4, param_extra=0.10)
        historial_reservas.append(res1)
        res1.procesar_reserva()
    except Exception as e:
        pass
    
    #Operación 8: Reseva Exitosa 2 (Equipo con seguro)
    try:
        print("8. Procesando reserva 3 (Servidor por tres días con seguro de $30)")
        res2 = Reserva(clientes_registrados[1], servicios_disponibles[1], 3, param_extra=30.0)
        historial_reservas.append(res2)
        res2.procesar_reserva()
    except Exception as e:
        pass
    
    #Operación 9: Reserva fallida (Duración invalida, hace que entre a la excepción y encadenamiento)
    try:
        print("9. Procesando reserva 4 (Asesoria con duración negativa)")
        res3 = Reserva(clientes_registrados[0], servicios_disponibles[2], -2, param_extra=0.0)
        historial_reservas.append(res3)
        res3.procesar_reserva()
    except Exception as e:
        print(f"Excepción capturada durante la reserva: {e}")
    
    #Operación 10: Cancelar una reserva confirmada y registro en logs
    try:
        print("10. Cancelando reserva la 1")
        if historial_reservas:
            historial_reservas[0].cancelar_reserva()
    except Exception as e:
        print(f"Error al cancelar la reserva: {e}")
        
    print("\n=== Fin de la simulación ===")
