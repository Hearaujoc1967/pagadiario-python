<?php

class Prestamo_model extends CI_Model {

	public function guardar_prestamo($id_estado_prestamo,$id_cobrador,$id_cliente,$id_tipo_prestamo,$id_metodo_pago,$porcentaje,$monto_prestado,$interes,$total_prestado,$numero_cuotas,$monto_x_cuotas,$fecha_prestamo){
		$data = array('id_estado_prestamo' =>$id_estado_prestamo,
		'id_cliente'=>$id_cliente,
		'id_cobrador'=>$id_cobrador,
		'id_tipo_prestamo'=>$id_tipo_prestamo,
		'id_metodo_pago'=>$id_metodo_pago,
		'porcentaje'=>$porcentaje,
		'monto_prestado'=>$monto_prestado,
		'interes'=>$interes,
		'total_prestado'=>$total_prestado,
		'numero_cuotas'=>$numero_cuotas,
		'monto_x_cuotas'=>$monto_x_cuotas,
		'fecha_prestamo'=>$fecha_prestamo
		 );
		$this->db->insert('t_prestamo', $data);
	}
	 public function contar_dias_atraso($id_prestamo){
        $this->db->from('t_atraso');
        $this->db->where('id_prestamo',$id_prestamo);
        return $this->db->count_all_results();
    }
   public function get_atraso_id_prestamo($id_prestamo){
   	$this->db->select('t_atraso.id as id_atraso, t_atraso.observaciones as observaciones, t_atraso.fecha as fecha_atraso, t_atraso.fecha_proximo_cobro as fecha_prox_cobro');
   	$this->db->where('t_atraso.id_prestamo', $id_prestamo);
   	$consulta=$this->db->get('t_atraso');
   	 if($consulta->num_rows() > 0){ 
   			return $consulta->result();
   	 }
   	
   }
	public function get_prestamo_id($id_prestamo){
		$this->db->select('t_prestamo.id as id_prestamo, t_prestamo.id_cliente as id_cliente, t_prestamo.porcentaje as porcentaje,t_prestamo.porcentaje_aprobado as porcentaje_aprobado, t_prestamo.monto_prestado as monto_prestado,, t_prestamo.monto_aprobado as monto_aprobado, t_prestamo.interes as interes_prestamo,t_prestamo.total_prestado as total_prestado,t_prestamo.numero_cuotas as numero_cuotas,t_prestamo.monto_x_cuotas as monto_x_cuotas,t_prestamo.cuotas_amortizadas as cuotas_amortizadas,t_prestamo.cuotas_debe as cuotas_debe,t_prestamo.atrasos as atrasos,t_prestamo.dias_mora as dias_mora,t_prestamo.penalidad as penalidad,t_prestamo.total_penalidad as total_penalidad,t_prestamo.total_debe as total_debe,t_prestamo.observacion as observacion,t_prestamo.fecha_prestamo as fecha_prestamo,t_prestamo.fecha_prox_cobro as fecha_prox_cobro, t_estado_prestamo.descripcion as estado_prestamo, t_cliente.dni as dni_cliente, t_cliente.nombre as nombre_cliente, t_cobrador.nombre as nombre_cobrador, t_tipo_prestamo.descripcion as tipo_prestamo, t_metodo_pago.descripcion as metodo_pago');
		$this->db->join('t_estado_prestamo', 't_prestamo.id_estado_prestamo = t_estado_prestamo.id', 'left');
		$this->db->join('t_cliente', 't_prestamo.id_cliente = t_cliente.id', 'left');
		$this->db->join('t_cobrador', 't_prestamo.id_cobrador = t_cobrador.id', 'left');
		$this->db->join('t_tipo_prestamo', 't_prestamo.id_tipo_prestamo = t_tipo_prestamo.id', 'left');
		$this->db->join('t_metodo_pago', 't_prestamo.id_metodo_pago = t_metodo_pago.id', 'left');
		$this->db->where('t_prestamo.id', $id_prestamo);
		$consulta=$this->db->get('t_prestamo',1);
		 if($consulta->num_rows() > 0){ 
				return $consulta->result();
				}
	}
  public function get_prestamo_id_cliente($id_cliente){
    $id_estado_prestamo='2';
    $this->db->select('t_prestamo.id as id_prestamo, t_prestamo.id_cliente as id_cliente, t_prestamo.porcentaje as porcentaje,t_prestamo.porcentaje_aprobado as porcentaje_aprobado, t_prestamo.monto_prestado as monto_prestado,, t_prestamo.monto_aprobado as monto_aprobado, t_prestamo.interes as interes_prestamo,t_prestamo.total_prestado as total_prestado,t_prestamo.numero_cuotas as numero_cuotas,t_prestamo.monto_x_cuotas as monto_x_cuotas,t_prestamo.cuotas_amortizadas as cuotas_amortizadas,t_prestamo.cuotas_debe as cuotas_debe,t_prestamo.atrasos as atrasos,t_prestamo.dias_mora as dias_mora,t_prestamo.penalidad as penalidad,t_prestamo.total_penalidad as total_penalidad,t_prestamo.total_debe as total_debe,t_prestamo.observacion as observacion,t_prestamo.fecha_prestamo as fecha_prestamo,t_prestamo.fecha_prox_cobro as fecha_prox_cobro, t_estado_prestamo.descripcion as estado_prestamo, t_cliente.dni as dni_cliente, t_cliente.nombre as nombre_cliente, t_cobrador.nombre as nombre_cobrador, t_tipo_prestamo.descripcion as tipo_prestamo, t_metodo_pago.descripcion as metodo_pago');
    $this->db->join('t_estado_prestamo', 't_prestamo.id_estado_prestamo = t_estado_prestamo.id', 'left');
    $this->db->join('t_cliente', 't_prestamo.id_cliente = t_cliente.id', 'left');
    $this->db->join('t_cobrador', 't_prestamo.id_cobrador = t_cobrador.id', 'left');
    $this->db->join('t_tipo_prestamo', 't_prestamo.id_tipo_prestamo = t_tipo_prestamo.id', 'left');
    $this->db->join('t_metodo_pago', 't_prestamo.id_metodo_pago = t_metodo_pago.id', 'left');
    $this->db->where('t_prestamo.id_estado_prestamo', $id_estado_prestamo);
    $this->db->where('t_prestamo.id_cliente', $id_cliente);
    $consulta=$this->db->get('t_prestamo',1);
     if($consulta->num_rows() > 0){ 
        return $consulta->result();
        }
  }
	public function actualizar_estado_prestamo_aprobado($id_prestamo,$id_estado_prestamo,$total_prestado,$porcentaje_aprobado,$interes,$nuevo_monto,$numero_cuotas_aprobadas,$monto_x_cuotas,$penalidad,$fecha_aprobacion_prestamo,$fecha_prox_cobro,$observaciones){
    $data = array('monto_aprobado'=>$total_prestado,
				'porcentaje_aprobado'=>$porcentaje_aprobado,
				'interes'=>$interes,
				'total_prestado'=>$total_prestado,
				'total_debe'=>$nuevo_monto,
				'numero_cuotas_aprobadas'=>$numero_cuotas_aprobadas,
				'monto_x_cuotas'=>$monto_x_cuotas,
				'cuotas_amortizadas'=>'0',
				'cuotas_debe'=>$numero_cuotas_aprobadas,
				'id_estado_prestamo'=>$id_estado_prestamo,
				'atrasos'=>$penalidad,
				'fecha_aprobacion_prestamo'=>$fecha_aprobacion_prestamo,
				'fecha_prox_cobro'=>$fecha_prox_cobro,
				'observacion'=>$observaciones);
		$this->db->where('id', $id_prestamo);
		$this->db->update('t_prestamo', $data);
	}
	public function guardar_abono($id_prestamo,$id_tipo_prestamo_2,$cuota_abonada,$observaciones,$monto,$fecha_cobro,$prox_pago){
  
		$data = array('id_prestamo'=>$id_prestamo,
				'id_tipo_prestamo_2'=>$id_tipo_prestamo_2,
				'cuota'=>$cuota_abonada,
				'descripcion'=>$observaciones,
				'monto'=>$monto,
				'fecha_cobro'=>$fecha_cobro,
				'fecha_prox_cobro'=>$prox_pago);
		$this->db->insert('t_det_prestamo', $data);
	}
		public function actualizar_abono_prestamo ($id_prestamo,$cuotas_amortizadas,$cuotas_debe,$fecha_cobro,$prox_pago,$nueva_deuda){
			$data = array(
				'cuotas_amortizadas'=>$cuotas_amortizadas,
				'cuotas_debe'=>$cuotas_debe,
				'total_debe'=>$nueva_deuda,
				'fecha_ultimo_cobro'=>$fecha_cobro,
				'fecha_prox_cobro'=>$prox_pago);
			$this->db->where('id', $id_prestamo);
			$this->db->update('t_prestamo',$data);
			
		}
		public function guardar_atraso($id_prestamo,$fecha,$fecha_prox_cobro,$observaciones){
			$data = array('id_prestamo' =>$id_prestamo,
			'observaciones'=>$observaciones,
			'fecha'=>$fecha,
			'fecha_proximo_cobro'=>$fecha_prox_cobro);
			$this->db->insert('t_atraso', $data);
		}
		
		public function actualizar_prestamo_dia_mora($id_prestamo,$fecha_prox_cobro,$suma_dias_mora){
			$data = array('fecha_prox_cobro' =>$fecha_prox_cobro,
			'dias_mora'=>$suma_dias_mora);
			$this->db->where('id', $id_prestamo);
			$this->db->update('t_prestamo', $data);
		}
		public function actualizar_prestamo_penalidad($id_prestamo,$fecha_prox_cobro,$penalidad,	$sumar_cuotas_debe,$suma_dias_mora){
			$data = array('cuotas_debe'=>$sumar_cuotas_debe,
				'fecha_prox_cobro' =>$fecha_prox_cobro,
				'dias_mora'=>$suma_dias_mora,
			'penalidad'=>$penalidad);
			$this->db->where('id', $id_prestamo);
			$this->db->update('t_prestamo', $data);	
		}

		public function get_det_prestamo_id($id_prestamo){
			$this->db->select('t_det_prestamo.id as id_det_prestamo, t_det_prestamo.cuota as cuota_det_prestamo, t_det_prestamo.descripcion as observaciones_det_prestamo, t_det_prestamo.monto as monto_det_prestamo, t_det_prestamo.fecha_cobro as fecha_cobro_det_prestamo, t_tipo_prestamo_2.descripcion as descripcion_tipo_prestamo');
			$this->db->where('t_det_prestamo.id_prestamo', $id_prestamo);
			$this->db->join('t_tipo_prestamo_2', 't_det_prestamo.id_tipo_prestamo_2 = t_tipo_prestamo_2.id', 'left');
			$consulta=$this->db->get('t_det_prestamo');
			 if($consulta->num_rows() > 0){ 
					return $consulta->result();
			  }
			
		}
		public function suma_dinero_recoger($fecha){
         $this->db->select_sum('monto_x_cuotas');
         $this->db->where('id_estado_prestamo', '2');
         $this->db->where('fecha_prox_cobro', $fecha);
         $consulta=$this->db->get('t_prestamo');
          if($consulta->num_rows() > 0){
            return $consulta->result();
        }
    }
    public function suma_dinero_recoger_cobrador($fecha,$id_cobrador){
         $this->db->select_sum('monto_x_cuotas');
        $this->db->where('id_estado_prestamo', '2');
         $this->db->where('id_cobrador', $id_cobrador);
         $this->db->where('fecha_prox_cobro', $fecha);
         $consulta=$this->db->get('t_prestamo');
          if($consulta->num_rows() > 0){
            return $consulta->result();
        }
    }
    public function suma_dinero_recogido($fecha){
         $this->db->select_sum('monto');
         $this->db->where('fecha_cobro',$fecha);
         $consulta=$this->db->get('t_det_prestamo');
          if($consulta->num_rows() > 0){
            return $consulta->result();
        }
    }
    public function suma_dinero_recogido_cobrador($fecha,$id_cobrador){
         $this->db->select('t_prestamo.id_cobrador as id_cobrador, SUM(t_det_prestamo.monto) as monto');
         ;
         $this->db->where('t_prestamo.id_cobrador', $id_cobrador);
         $this->db->where('t_det_prestamo.fecha_cobro',$fecha);
         $this->db->join('t_prestamo', 't_det_prestamo.id_prestamo = t_prestamo.id', 'left');
         $consulta=$this->db->get('t_det_prestamo');
          if($consulta->num_rows() > 0){
            return $consulta->result();
        }
    }
     public function contar_atrasos($fecha){
            $this->db->from('t_prestamo');
            $this->db->where('id_estado_prestamo', '2');
            $this->db->where('fecha_ultimo_cobro <',$fecha);
            $this->db->or_where('fecha_prox_cobro <',$fecha);
          
            return $this->db->count_all_results();
    }
    public function contar_atrasos_cobrador($fecha,$id_cobrador){
            $this->db->from('t_prestamo');
            $this->db->where('id_cobrador', $id_cobrador);
            $this->db->where('id_estado_prestamo', '2');
            $this->db->where('fecha_ultimo_cobro <',$fecha);
            $this->db->or_where('fecha_prox_cobro <',$fecha);
            
            return $this->db->count_all_results();
    }
    public function prestamos_x_aprobar(){
            $this->db->from('t_prestamo');
            $this->db->where('id_estado_prestamo',1);
            return $this->db->count_all_results();
    }
    public function sumar_pagos_entre_fechas($fecha_i, $fecha_f){
			$this->db->select('fecha_cobro as fecha, sum(monto) as total');
			$this->db->group_by('fecha');
      $this->db->where('fecha_cobro >=',$fecha_i);
      $this->db->where('fecha_cobro <=',$fecha_f);
      $consulta=$this->db->get('t_det_prestamo');
      if($consulta->num_rows() > 0){
            return $consulta->result();
        }
    }
    public function sumar_pagos_entre_fechas_cobrador($id_cobrador, $fecha_i, $fecha_f){
			$this->db->select('t_det_prestamo.fecha_cobro as fecha, sum(t_det_prestamo.monto) as total');
			$this->db->group_by('fecha');
			 $this->db->where('t_prestamo.id_cobrador', $id_cobrador);
      $this->db->where('t_det_prestamo.fecha_cobro >=',$fecha_i);
      $this->db->where('t_det_prestamo.fecha_cobro <=',$fecha_f);
      $this->db->join('t_prestamo', 't_det_prestamo.id_prestamo = t_prestamo.id', 'left');
         $consulta=$this->db->get('t_det_prestamo');
          if($consulta->num_rows() > 0){
            return $consulta->result();
        }
    }
    public function contar_prestamos($fecha_i, $fecha_f){
			$this->db->select('fecha_aprobacion_prestamo as fecha, count(id) as total');
			$this->db->group_by('fecha');
      $this->db->where('fecha_aprobacion_prestamo >=',$fecha_i);
      $this->db->where('fecha_aprobacion_prestamo <=',$fecha_f);

      $consulta=$this->db->get('t_prestamo');
      if($consulta->num_rows() > 0){
            return $consulta->result();
        }
    }
     public function sumar_pagos_cierre_x_cobrador($id_cobrador, $fecha){
			$this->db->select('t_det_prestamo.fecha_cobro as fecha, sum(t_det_prestamo.monto) as total');
			$this->db->group_by('fecha');
			$this->db->where('t_prestamo.id_cobrador', $id_cobrador);
      $this->db->where('t_det_prestamo.fecha_cobro ',$fecha);
      $this->db->join('t_prestamo', 't_det_prestamo.id_prestamo = t_prestamo.id', 'left');
         $consulta=$this->db->get('t_det_prestamo');
          if($consulta->num_rows() > 0){
            return $consulta->result();
        }
    }
    public function sumar_pagos_cierre_x_cobrador_por_fecha_total($id_cobrador, $fecha_i, $fecha_f){
      $this->db->select('t_det_prestamo.fecha_cobro as fecha, sum(t_det_prestamo.monto) as total');
      $this->db->where('t_prestamo.id_cobrador', $id_cobrador);
      $this->db->where('t_det_prestamo.fecha_cobro  >=',$fecha_i);
      $this->db->where('t_det_prestamo.fecha_cobro  <=',$fecha_f);
      $this->db->join('t_prestamo', 't_det_prestamo.id_prestamo = t_prestamo.id', 'left');
         $consulta=$this->db->get('t_det_prestamo');
          if($consulta->num_rows() > 0){
            return $consulta->result();
        }
    }
    public function sumar_pagos_cierre_x_cobrador_por_fecha($id_cobrador, $fecha_i, $fecha_f){
      $this->db->select('t_det_prestamo.fecha_cobro as fecha, sum(t_det_prestamo.monto) as total');
      $this->db->group_by('fecha');
      $this->db->where('t_prestamo.id_cobrador', $id_cobrador);
      $this->db->where('t_det_prestamo.fecha_cobro  >=',$fecha_i);
      $this->db->where('t_det_prestamo.fecha_cobro  <=',$fecha_f);
      $this->db->join('t_prestamo', 't_det_prestamo.id_prestamo = t_prestamo.id', 'left');
         $consulta=$this->db->get('t_det_prestamo');
          if($consulta->num_rows() > 0){
            return $consulta->result();
        }
    }
      public function sumar_pagos_por_fecha($fecha){
      $this->db->select('t_det_prestamo.fecha_cobro as fecha, sum(t_det_prestamo.monto) as total');
      $this->db->group_by('fecha');
      $this->db->where('t_det_prestamo.fecha_cobro ',$fecha);
      $this->db->join('t_prestamo', 't_det_prestamo.id_prestamo = t_prestamo.id', 'left');
         $consulta=$this->db->get('t_det_prestamo');
          if($consulta->num_rows() > 0){
            return $consulta->result();
        }
    }
     public function get_pagos_x_cobrador($id_cobrador, $fecha){
			$this->db->select('t_cliente.nombre as nombre_cliente, t_det_prestamo.fecha_cobro as fecha, t_det_prestamo.monto as monto');
			$this->db->where('t_prestamo.id_cobrador', $id_cobrador);
      $this->db->where('t_det_prestamo.fecha_cobro ',$fecha);
      $this->db->join('t_det_prestamo', 't_prestamo.id=t_det_prestamo.id_prestamo', 'right');
      $this->db->join('t_cliente', 't_prestamo.id_cliente = t_cliente.id', 'left');
      $consulta=$this->db->get('t_prestamo');
          if($consulta->num_rows() > 0){
            return $consulta->result();
        }
    }
    /*busca atraso por cobrador no lo estoy utilizando*/
    public function get_atraso_x_cobrador($id_cobrador, $fecha){
			$this->db->select('t_cliente.nombre as nombre_cliente, t_atraso.fecha as fecha, t_atraso.observaciones as observaciones');
			$this->db->where('t_prestamo.id_cobrador', $id_cobrador);
      $this->db->where('t_atraso.fecha ',$fecha);
      $this->db->join('t_prestamo', 't_atraso.id_prestamo = t_prestamo.id', 'left');
      $this->db->join('t_cliente', 't_prestamo.id_cliente = t_cliente.id', 'left');
         $consulta=$this->db->get('t_atraso');
          if($consulta->num_rows() > 0){
            return $consulta->result();
        }
    }
    public function actualizar_estado_prestamo($id_prestamo_anterior,$estado_prestamo,$total_debe){
    
      $data = array('id_estado_prestamo' =>$estado_prestamo,
        'total_debe'=>$total_debe,);
      $this->db->where('id', $id_prestamo_anterior);
      $this->db->update('t_prestamo', $data);
      
    }
    public function actualizar_estado_prestamo_finalizado($id_prestamo_anterior,$estado_prestamo,$cuotas_debe, $total_debe){
      $data = array('id_estado_prestamo' =>$estado_prestamo,
        'cuotas_debe'=>$cuotas_debe,
        'total_debe'=>$total_debe);
      $this->db->where('id', $id_prestamo_anterior);
      $this->db->update('t_prestamo', $data);
      
    }

/* End of file prestamo_model.php */
/* Location: ./application/models/prestamo_model.php */
}
